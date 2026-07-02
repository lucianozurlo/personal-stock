import json
import logging
import time
from datetime import datetime, timezone
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from core.helpers.conversation import ConversationIdManager
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from core.models import WorkflowRun
from core.services import MetricsAggregator, PermissionChecker, TraceabilityManager
from core.helpers.user_object import UserObjectBuilder
from core.helpers.html_sanitizer import HTMLSanitizer
from core.serializers.chat_serializers import RequestPayloadSerializer, ResponsePayloadSerializer
from core.clients.n8n_client import (
    N8nClient,
    N8nClientError,
    N8nConnectionError,
    N8nTimeoutError,
    N8nInvalidResponseError,
)

logger = logging.getLogger(__name__)


def api_login_required(view_func):
    """
    Como login_required, pero para endpoints /api/*: responde 401 JSON en vez de
    redirigir a /login/ (Requirement 4.6 de acciones-trazabilidad-metricas).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Autenticación requerida'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if remember_me:
                request.session.set_expiry(1209600)  # 2 semanas
            else:
                request.session.set_expiry(0)  # sesión de navegador
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Email o contraseña incorrectos'})

    return render(request, 'login.html')


@login_required
def home_view(request):
    user = request.user
    roles_list = list(user.roles.values_list('name', flat=True))
    context = {
        'user': user,
        'perfil': user.perfil,
        'roles': user.roles.all(),
        'ps_user_data': {
            'firstName': user.first_name or user.username,
            'username': user.username,
            'email': user.email,
            'perfil': user.perfil,
            'roles': roles_list,
        }
    }
    return render(request, 'home.html', context)


def logout_view(request):
    logout(request)
    return redirect('/login/')


@login_required
@require_http_methods(["POST"])
@csrf_protect
def chat_view(request):
    run_id = None
    start_time = time.time()

    try:
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        query = body.get('query', '').strip()
        agent_type = body.get('agentType', 'auto')

        if not query:
            return JsonResponse({'error': 'Query is required'}, status=400)

        conversation_id = ConversationIdManager.get_or_create(request.session)
        user_object = UserObjectBuilder.build(request.user)

        run = TraceabilityManager.create_run(
            user=request.user,
            conversation_id=conversation_id,
            user_message=query,
            agent_type=agent_type,
        )
        run_id = run.id if run else None

        # 8.4: Construir Request_Payload
        request_payload = {
            'conversationId': conversation_id,
            'query': query,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'user': user_object,
            'agentType': agent_type,
        }

        # 8.4: Validar Request_Payload con serializer
        serializer = RequestPayloadSerializer(data=request_payload)
        if not serializer.is_valid():
            logger.error("Payload validation failed: %s", serializer.errors)
            return JsonResponse(
                {'error': 'Validation failed', 'details': serializer.errors},
                status=400
            )

        validated_payload = serializer.validated_data

        # 8.5: Enviar a n8n con N8nClient
        try:
            client = N8nClient()
            response_data = client.send(validated_payload)
        except N8nTimeoutError as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            if run_id:
                TraceabilityManager.fail_run(run_id, f"n8n timeout: {str(e)}", execution_time_ms)
            logger.error(
                "N8n request timed out",
                extra={
                    'user_id': request.user.id,
                    'conversation_id': conversation_id,
                    'query': query[:100],
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                },
            )
            return JsonResponse(
                {'error': 'El sistema tardó demasiado en responder. Por favor, intentá de nuevo.'},
                status=504,
            )
        except N8nInvalidResponseError as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            if run_id:
                TraceabilityManager.fail_run(run_id, f"n8n invalid response: {str(e)}", execution_time_ms)
            logger.error(
                "N8n invalid response",
                extra={
                    'user_id': request.user.id,
                    'conversation_id': conversation_id,
                    'query': query[:100],
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                },
            )
            return JsonResponse(
                {'error': f'Error procesando respuesta de n8n: {str(e)}'},
                status=502,
            )
        except (ValueError, N8nConnectionError) as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            if run_id:
                TraceabilityManager.fail_run(run_id, f"n8n unavailable: {str(e)}", execution_time_ms)
            logger.error(
                "N8n unavailable",
                extra={
                    'user_id': request.user.id,
                    'conversation_id': conversation_id,
                    'query': query[:100],
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                },
            )
            return JsonResponse(
                {'error': f'Error conectando con n8n: {str(e)}'},
                status=503,
            )
        except N8nClientError as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            if run_id:
                TraceabilityManager.fail_run(run_id, f"n8n client error: {str(e)}", execution_time_ms)
            logger.error(
                "N8n client error",
                extra={
                    'user_id': request.user.id,
                    'conversation_id': conversation_id,
                    'query': query[:100],
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                },
            )
            return JsonResponse(
                {'error': f'Error conectando con n8n: {str(e)}'},
                status=503,
            )

        # 8.6: Sanitizar HTML (defense in depth — zero trust external systems)
        if 'output' in response_data:
            response_data['output'] = HTMLSanitizer.sanitize(response_data['output'])

        # 8.6: Validar Response_Payload
        response_serializer = ResponsePayloadSerializer(data=response_data)
        if not response_serializer.is_valid():
            logger.error("Response validation failed: %s", response_serializer.errors)
            execution_time_ms = int((time.time() - start_time) * 1000)
            if run_id:
                TraceabilityManager.fail_run(
                    run_id,
                    f"Invalid n8n response: {response_serializer.errors}",
                    execution_time_ms,
                )
            return JsonResponse(
                {'error': 'Invalid response from orchestrator'},
                status=502,
            )

        execution_time_ms = int((time.time() - start_time) * 1000)

        # Req 9.6: Poblar metadata desde WorkflowRun (override execution_time_ms con tiempo medido end-to-end)
        validated_response = dict(response_serializer.validated_data)
        if 'metadata' in validated_response:
            validated_response['metadata'] = dict(validated_response['metadata'])
            validated_response['metadata']['execution_time_ms'] = execution_time_ms

        if run_id:
            TraceabilityManager.complete_run(
                run_id=run_id,
                agent_response=str(validated_response.get('output', '')),
                execution_time_ms=execution_time_ms,
                metadata=dict(validated_response.get('metadata', {})),
            )

        logger.info(
            "Chat request processed successfully",
            extra={
                'user_id': request.user.id,
                'conversation_id': conversation_id,
                'query': query[:100],
                'agent_used': validated_response.get('metadata', {}).get('agent_used', 'unknown'),
            },
        )
        return JsonResponse(validated_response, status=200)

    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        if run_id:
            TraceabilityManager.fail_run(run_id, str(e), execution_time_ms)
        logger.exception("Unexpected error in chat_view")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@api_login_required
@require_http_methods(["GET"])
def api_actions(request):
    try:
        page = request.GET.get('page', 1)
        page_size = min(int(request.GET.get('page_size', 20)), 100)

        qs = PermissionChecker.get_user_runs_queryset(request.user)
        paginator = Paginator(qs, page_size)

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            return JsonResponse({'error': 'Número de página inválido'}, status=400)
        except EmptyPage:
            return JsonResponse({'error': 'Página fuera de rango'}, status=404)

        base_url = request.build_absolute_uri(request.path)
        next_url = (
            f"{base_url}?page={page_obj.next_page_number()}&page_size={page_size}"
            if page_obj.has_next() else None
        )
        prev_url = (
            f"{base_url}?page={page_obj.previous_page_number()}&page_size={page_size}"
            if page_obj.has_previous() else None
        )

        results = [
            {
                'id': run.id,
                'user_message': run.user_message[:100],
                'detected_intention': run.detected_intention,
                'selected_agent': run.selected_agent,
                'final_state': run.final_state,
                'timestamp': run.created_at.isoformat(),
                'execution_time_ms': run.execution_time_ms,
            }
            for run in page_obj
        ]

        return JsonResponse({
            'count': paginator.count,
            'next': next_url,
            'previous': prev_url,
            'results': results,
        }, status=200)

    except Exception:
        logger.exception("Unexpected error in api_actions")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@api_login_required
@require_http_methods(["GET"])
def api_action_detail(request, action_id):
    run = get_object_or_404(WorkflowRun, id=action_id, user=request.user)

    try:
        return JsonResponse({
            'id': run.id,
            'user_message': run.user_message,
            'agent_response': run.agent_response,
            'system_decisions': run.system_decisions,
            'permissions_applied': run.permissions_applied,
            'error_message': run.error_message,
            'final_state': run.final_state,
            'timestamp': run.created_at.isoformat(),
        }, status=200)

    except Exception:
        logger.exception("Unexpected error in api_action_detail")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@api_login_required
@require_http_methods(["GET"])
def api_metrics(request):
    if not PermissionChecker.can_access_metrics(request.user):
        return JsonResponse(
            {'error': 'No tiene permisos para acceder a las métricas'},
            status=403,
        )

    try:
        start_date = None
        end_date = None

        if request.GET.get('start_date'):
            try:
                start_date = datetime.fromisoformat(request.GET['start_date'])
            except ValueError:
                return JsonResponse(
                    {'error': 'Formato de fecha inválido. Use ISO 8601.'},
                    status=400,
                )

        if request.GET.get('end_date'):
            try:
                end_date = datetime.fromisoformat(request.GET['end_date'])
            except ValueError:
                return JsonResponse(
                    {'error': 'Formato de fecha inválido. Use ISO 8601.'},
                    status=400,
                )

        metrics = MetricsAggregator.get_summary_metrics(start_date, end_date)
        return JsonResponse(metrics, status=200)

    except Exception:
        logger.exception("Unexpected error in api_metrics")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@api_login_required
@require_http_methods(["GET"])
def api_admin_actions(request):
    if not PermissionChecker.can_access_admin_actions(request.user):
        return JsonResponse(
            {'error': 'Solo los administradores pueden acceder a esta información'},
            status=403,
        )

    try:
        page = request.GET.get('page', 1)
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        raw_user_id = request.GET.get('user_id')
        user_id = int(raw_user_id) if raw_user_id else None

        qs = PermissionChecker.get_all_runs_queryset(user_id).select_related('user')
        paginator = Paginator(qs, page_size)

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            return JsonResponse({'error': 'Número de página inválido'}, status=400)
        except EmptyPage:
            return JsonResponse({'error': 'Página fuera de rango'}, status=404)

        base_url = request.build_absolute_uri(request.path)
        next_url = (
            f"{base_url}?page={page_obj.next_page_number()}&page_size={page_size}"
            if page_obj.has_next() else None
        )
        prev_url = (
            f"{base_url}?page={page_obj.previous_page_number()}&page_size={page_size}"
            if page_obj.has_previous() else None
        )

        results = [
            {
                'id': run.id,
                'user_id': run.user_id,
                'user_email': run.user.email,
                'user_name': run.user.get_full_name() or run.user.username,
                'user_message': run.user_message[:100],
                'detected_intention': run.detected_intention,
                'selected_agent': run.selected_agent,
                'permissions_applied': run.permissions_applied,
                'system_decisions': run.system_decisions,
                'final_state': run.final_state,
                'timestamp': run.created_at.isoformat(),
                'execution_time_ms': run.execution_time_ms,
            }
            for run in page_obj
        ]

        return JsonResponse({
            'count': paginator.count,
            'next': next_url,
            'previous': prev_url,
            'results': results,
        }, status=200)

    except Exception:
        logger.exception("Unexpected error in api_admin_actions")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@login_required
@require_http_methods(["GET"])
def actions_page(request):
    page = request.GET.get('page', 1)
    qs = PermissionChecker.get_user_runs_queryset(request.user)
    paginator = Paginator(qs, 20)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'actions.html', {'page_obj': page_obj, 'user': request.user})
