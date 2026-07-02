import logging
from typing import Optional

from django.db import transaction
from django.db.models import Avg, Count

from core.models import MetricEvent, User, WorkflowRun

logger = logging.getLogger(__name__)


class TraceabilityManager:

    @staticmethod
    def create_run(
        user,
        conversation_id: str,
        user_message: str,
        agent_type: str,
    ) -> Optional[WorkflowRun]:
        try:
            with transaction.atomic():
                run = WorkflowRun.objects.create(
                    user=user,
                    conversation_id=conversation_id,
                    user_message=user_message,
                    selected_agent=agent_type,
                )
                run.add_state_transition(WorkflowRun.ExecutionState.CREATED)
                run.save()
                return run
        except Exception:
            logger.error("Failed to create WorkflowRun", exc_info=True)
            return None

    @staticmethod
    def update_run_agent_selection(
        run_id: int,
        detected_intention: str,
        selected_agent: str,
        selection_reason: str,
        permissions_applied: str,
    ) -> None:
        try:
            with transaction.atomic():
                run = WorkflowRun.objects.select_for_update().get(id=run_id)
                run.detected_intention = detected_intention
                run.selected_agent = selected_agent
                run.selection_reason = selection_reason
                run.permissions_applied = permissions_applied
                run.add_state_transition(WorkflowRun.ExecutionState.RUNNING)
                run.save()
        except WorkflowRun.DoesNotExist:
            logger.warning("WorkflowRun %s not found for agent selection update", run_id)
        except Exception:
            logger.error("Failed to update WorkflowRun agent selection for run %s", run_id, exc_info=True)

    @staticmethod
    def complete_run(
        run_id: int,
        agent_response: str,
        execution_time_ms: int,
        metadata: dict,
    ) -> None:
        try:
            with transaction.atomic():
                run = WorkflowRun.objects.select_for_update().get(id=run_id)
                run.agent_response = agent_response
                run.execution_time_ms = execution_time_ms
                if metadata:
                    existing = run.system_decisions or {}
                    existing['response_metadata'] = metadata
                    run.system_decisions = existing
                    if metadata.get('agent_used'):
                        run.selected_agent = metadata['agent_used']
                run.add_state_transition(WorkflowRun.ExecutionState.COMPLETED)
                run.save()
        except WorkflowRun.DoesNotExist:
            logger.warning("WorkflowRun %s not found for complete_run", run_id)
        except Exception:
            logger.error("Failed to complete WorkflowRun %s", run_id, exc_info=True)

    @staticmethod
    def fail_run(
        run_id: int,
        error_message: str,
        execution_time_ms: int,
    ) -> None:
        try:
            with transaction.atomic():
                run = WorkflowRun.objects.select_for_update().get(id=run_id)
                run.error_message = error_message
                run.execution_time_ms = execution_time_ms
                run.add_state_transition(WorkflowRun.ExecutionState.FAILED)
                run.save()
        except WorkflowRun.DoesNotExist:
            logger.warning("WorkflowRun %s not found for fail_run", run_id)
        except Exception:
            logger.error("Failed to mark WorkflowRun %s as failed", run_id, exc_info=True)


class MetricsAggregator:

    @staticmethod
    def get_summary_metrics(
        start_date=None,
        end_date=None,
    ) -> dict:
        qs = WorkflowRun.objects.all()
        if start_date:
            qs = qs.filter(created_at__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__lte=end_date)

        total = qs.count()

        by_agent = dict(
            qs.values('selected_agent')
              .annotate(count=Count('id'))
              .values_list('selected_agent', 'count')
        )

        by_state = dict(
            qs.values('final_state')
              .annotate(count=Count('id'))
              .values_list('final_state', 'count')
        )

        avg_time = dict(
            qs.exclude(execution_time_ms__isnull=True)
              .values('selected_agent')
              .annotate(avg_ms=Avg('execution_time_ms'))
              .values_list('selected_agent', 'avg_ms')
        )

        error_rate = {}
        for agent in by_agent.keys():
            agent_total = qs.filter(selected_agent=agent).count()
            agent_failed = qs.filter(
                selected_agent=agent,
                final_state=WorkflowRun.ExecutionState.FAILED,
            ).count()
            error_rate[agent] = agent_failed / agent_total if agent_total > 0 else 0.0

        return {
            'total_executions': total,
            'executions_by_agent': by_agent,
            'executions_by_state': by_state,
            'avg_execution_time_ms': avg_time,
            'error_rate': error_rate,
        }

    @staticmethod
    def record_metric_event(
        event_type: str,
        agent: Optional[str] = None,
        value: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        try:
            with transaction.atomic():
                MetricEvent.objects.create(
                    event_type=event_type,
                    agent=agent,
                    value=value,
                    metadata=metadata or {},
                )
        except Exception:
            logger.error("Failed to create MetricEvent", exc_info=True)


class PermissionChecker:

    @staticmethod
    def can_access_metrics(user) -> bool:
        return user.perfil in [User.Profile.ADMINISTRADOR, User.Profile.USUARIO_IC]

    @staticmethod
    def can_access_admin_actions(user) -> bool:
        return user.perfil == User.Profile.ADMINISTRADOR

    @staticmethod
    def get_user_runs_queryset(user):
        return WorkflowRun.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def get_all_runs_queryset(user_id: Optional[int] = None):
        queryset = WorkflowRun.objects.all().order_by('-created_at')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset
