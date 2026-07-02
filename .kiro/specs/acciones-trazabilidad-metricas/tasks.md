# Implementation Plan: Acciones, Trazabilidad y Métricas

## Overview

Este plan implementa el sistema de trazabilidad y métricas obligatorio para Personal Stock MVP 1. El sistema registra automáticamente TODA ejecución iniciada desde `/api/chat/` mediante dos modelos Django (WorkflowRun y MetricEvent), expone 3 endpoints REST (`/api/actions/`, `/api/metrics/`, `/api/admin/actions/`) y una página web de acciones (`/actions/`).

La integración con `/api/chat/` es transparente y obligatoria: el endpoint crea y actualiza WorkflowRun automáticamente en cada request mediante transacción separada síncrona. Usa las constantes `User.Profile.ADMINISTRADOR` y `User.Profile.USUARIO_IC` del modelo User (spec usuarios-demo-perfiles-permisos) para todas las comparaciones de perfil, no strings literales.

## Tasks

- [x] 1. Create Django models for traceability and metrics
  - [x] 1.1 Create WorkflowRun model in core/models.py
    - Define ExecutionState TextChoices with 12 states (created, running, needs_input, waiting_human, pending_approval, approved, rejected, blocked_by_permissions, blocked_by_compliance, failed, cancelled, completed)
    - Define all fields: user (ForeignKey), conversation_id, created_at, updated_at, execution_time_ms, user_message, detected_intention, selected_agent, selection_reason, permissions_applied, system_decisions (JSONField), agent_response, error_message, final_state, state_history (JSONField)
    - Add Meta with verbose_name, ordering by -created_at, and 4 indexes: (user, -created_at), final_state, selected_agent, created_at
    - Implement `add_state_transition(new_state)` method to update state_history and final_state
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10_

  - [x] 1.2 Create MetricEvent model in core/models.py
    - Define EventType TextChoices with 3 types (agent_execution, agent_error, permission_blocked)
    - Define all fields: event_type, agent, timestamp, value, metadata (JSONField)
    - Add Meta with verbose_name, ordering by -timestamp, and 2 indexes: (event_type, timestamp), (agent, timestamp)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 1.3 Create and run Django migrations
    - Run `python manage.py makemigrations core` to create migration files
    - Run `python manage.py migrate` to apply migrations
    - Verify models in Django shell: import and count both models
    - _Requirements: 1.1, 8.1_

- [x] 2. Checkpoint - Verify database setup
  - Ensure migrations applied successfully, verify indexes exist using `_meta.indexes`, report verification results point by point.

- [x] 3. Implement service classes for traceability and metrics
  - [x] 3.1 Create TraceabilityManager service class in core/services.py
    - Implement `create_run(user, conversation_id, user_message, agent_type)` method using `transaction.atomic()` for separate sync transaction, return Optional[WorkflowRun], log errors but don't propagate
    - Implement `update_run_agent_selection(run_id, detected_intention, selected_agent, selection_reason, permissions_applied)` method to transition state from created to running
    - Implement `complete_run(run_id, agent_response, execution_time_ms, metadata)` method to transition state from running to completed
    - Implement `fail_run(run_id, error_message, execution_time_ms)` method to transition state to failed
    - All methods must use WorkflowRun.add_state_transition() to update state_history
    - _Requirements: 1.1, 1.2, 2.2, 2.3, 2.4, 2.5, 2.9, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [x] 3.2 Create MetricsAggregator service class in core/services.py
    - Implement `get_summary_metrics(start_date, end_date)` method using Django ORM aggregation (Count, Avg, annotate, values) to return dict with: total_executions, executions_by_agent, executions_by_state, avg_execution_time_ms, error_rate
    - Implement `record_metric_event(event_type, agent, value, metadata)` method to create MetricEvent
    - Use efficient SQL queries with filters (created_at**gte, created_at**lte) and aggregation
    - _Requirements: 5.3, 5.6, 8.2, 8.3, 8.4, 8.6_

  - [x] 3.3 Create PermissionChecker service class in core/services.py
    - **CRITICAL**: Import `from core.models import User` and use `User.Profile.ADMINISTRADOR` and `User.Profile.USUARIO_IC` constants (NOT literal strings) for all profile comparisons
    - Implement `can_access_metrics(user)` method returning bool, checking if user.perfil in [User.Profile.ADMINISTRADOR, User.Profile.USUARIO_IC]
    - Implement `can_access_admin_actions(user)` method returning bool, checking if user.perfil == User.Profile.ADMINISTRADOR
    - Implement `get_user_runs_queryset(user)` method returning WorkflowRun.objects.filter(user=user).order_by('-created_at')
    - Implement `get_all_runs_queryset(user_id)` method returning all WorkflowRun ordered by -created_at, optionally filtered by user_id
    - _Requirements: 4.2, 5.2, 10.2_

- [x] 4. Checkpoint - Verify service classes
  - Ensure all service classes have correct methods, verify transaction handling in TraceabilityManager, report verification results point by point.

- [x] 5. Integrate traceability into /api/chat/ endpoint
  - [x] 5.1 Modify chat_view in core/views.py to add traceability
    - Import TraceabilityManager at top of file
    - Add run_id = None and start_time = time.time() at beginning of function
    - Call TraceabilityManager.create_run() after parsing request body, before calling n8n, store result in run and set run_id = run.id if run else None
    - After successful n8n response, call TraceabilityManager.complete_run() with run_id, agent_response, execution_time_ms, metadata
    - In all exception handlers (N8nTimeoutError, ConnectionError, etc.), call TraceabilityManager.fail_run() with run_id, error message, execution_time_ms
    - In final catch-all exception handler, also call TraceabilityManager.fail_run()
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [x] 5.2 Update response payload in chat_view to include metadata
    - Ensure response JSON includes metadata object with fields: agent_used, execution_time_ms, records_found (populated from WorkflowRun after agent completes)
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 6. Checkpoint - Test traceability integration
  - Ensure WorkflowRun is created on every /api/chat/ request, verify state transitions work correctly, report verification results point by point.

- [x] 7. Implement API endpoints for actions and metrics
  - [x] 7.1 Create api_actions view in core/views.py
    - Add @login_required and @require_http_methods(["GET"]) decorators
    - Parse page and page_size query params (defaults: page=1, page_size=20)
    - Use PermissionChecker.get_user_runs_queryset(request.user) to get filtered queryset
    - Apply pagination using Django Paginator
    - Return JsonResponse with structure: {count, next, previous, results: [{id, user_message, detected_intention, selected_agent, final_state, timestamp, execution_time_ms}]}
    - Handle errors: PageNotAnInteger (400), EmptyPage (404), generic Exception (500)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [x] 7.2 Create api_metrics view in core/views.py
    - Add @login_required and @require_http_methods(["GET"]) decorators
    - Check permissions using PermissionChecker.can_access_metrics(request.user), return 403 if false with error message "No tiene permisos para acceder a las métricas"
    - Parse start_date and end_date query params (ISO 8601 format)
    - Call MetricsAggregator.get_summary_metrics(start_date, end_date)
    - Return JsonResponse with metrics dict
    - Handle date parsing errors (400), generic exceptions (500)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [x] 7.3 Create api_admin_actions view in core/views.py
    - Add @login_required and @require_http_methods(["GET"]) decorators
    - Check permissions using PermissionChecker.can_access_admin_actions(request.user), return 403 if false with error message "Solo los administradores pueden acceder a esta información"
    - Parse page, page_size, and user_id query params
    - Use PermissionChecker.get_all_runs_queryset(user_id) to get queryset
    - Apply pagination using Django Paginator
    - Return JsonResponse with same structure as api_actions but include additional fields: user_id, user_email, user_name, permissions_applied, system_decisions
    - Handle errors: PageNotAnInteger (400), EmptyPage (404), generic Exception (500)
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

  - [x] 7.4 Add URL routes to core/urls.py
    - Add path('api/actions/', views.api_actions, name='api_actions')
    - Add path('api/metrics/', views.api_metrics, name='api_metrics')
    - Add path('api/admin/actions/', views.api_admin_actions, name='api_admin_actions')
    - _Requirements: 4.1, 5.1, 10.1_

- [x] 8. Checkpoint - Test API endpoints
  - Ensure all API endpoints return correct data, verify permissions work correctly, test pagination, report verification results point by point.

- [x] 9. Create actions template and page
  - [x] 9.1 Create actions.html template in templates/actions.html
    - Create HTML structure with header (logo, user name), main section with actions list, pagination controls, and modal div for details
    - Use Django template tags: {% load static %}, {% for action in page_obj %}, {% empty %}, {% if page_obj.has_previous/has_next %}
    - Add color coding with CSS classes: state-{{ action.final_state }} on each action card
    - Display for each action: timestamp (created_at|date:"d/m/Y H:i"), state badge (get_final_state_display), user_message (truncatewords:20), selected_agent, execution_time_ms
    - Add pagination links with previous/next page numbers
    - Include CSS link to {% static 'css/actions.css' %} and JS link to {% static 'js/actions.js' %}
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [x] 9.2 Create actions.css in templates/css/actions.css
    - Define color coding for states: .state-completed (green border-left: 4px solid #22c55e), .state-failed (red #ef4444), .state-running (blue #3b82f6), .state-pending_approval (yellow #eab308)
    - Add all blocked*by*\* and cancelled states using red color (same as failed)
    - Define styles for action cards, header, pagination controls, modal
    - Use responsive layout with flexbox/grid
    - _Requirements: 6.4_

  - [x] 9.3 Create actions.js in templates/js/actions.js
    - Implement showDetails(actionId) function to fetch action details via AJAX and display in modal
    - Create endpoint /api/actions/<id>/ to return full action details (optional for MVP 1, can be placeholder)
    - _Requirements: 6.5_

  - [x] 9.4 Create actions_page view in core/views.py
    - Add @login_required decorator
    - Parse page query param (default=1)
    - Get WorkflowRun.objects.filter(user=request.user).order_by('-created_at')
    - Apply pagination with 20 items per page
    - Render template 'actions.html' with context: {page_obj, user}
    - _Requirements: 6.1, 6.2, 6.6, 6.7_

  - [x] 9.5 Add URL route for actions page to core/urls.py
    - Add path('actions/', views.actions_page, name='actions_page')
    - _Requirements: 6.1_

- [x] 10. Checkpoint - Test actions page
  - Ensure actions page renders correctly, verify color coding works, test pagination, verify login required, report verification results point by point.

- [x] 11. Write unit tests for service classes
  - [x] 11.1 Write unit tests for TraceabilityManager in core/tests.py (módulo único; ver docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md — Python no permite coexistir core/tests.py y core/tests/, y ~15 devoluciones posteriores referencian core.tests.NombreClase)
    - test_create_run_sets_initial_state: verify final_state='created' and state_history has initial entry
    - test_update_run_agent_selection_transitions_to_running: verify state transition created → running
    - test_complete_run_sets_final_state: verify final_state='completed' and execution_time_ms saved
    - test_fail_run_records_error_message: verify final_state='failed' and error_message saved
    - _Requirements: 1.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 11.2 Write unit tests for MetricsAggregator in core/tests.py (módulo único; ver docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md — mismo criterio que 11.1, Python no permite coexistir core/tests.py y core/tests/)
    - test_metrics_aggregator_counts_executions_by_agent: create 3 runs with different agents, verify executions_by_agent counts
    - test_metrics_aggregator_filters_by_date_range: create runs with different timestamps, verify date filtering works
    - _Requirements: 5.3, 5.4, 5.6_

- [x] 12. Write integration tests for API endpoints
  - [x] 12.1 Write integration tests for /api/actions/ in core/tests.py (módulo único; ver docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md — mismo criterio que 11.x)
    - test_api_actions_returns_only_user_runs: create 2 users with runs, verify user1 only sees their own runs
    - test_api_actions_requires_authentication: verify HTTP 401 when not authenticated
    - test_api_actions_paginates_results: create 25 runs, verify response has 20 items and next link
    - _Requirements: 4.2, 4.5, 4.6_

  - [x] 12.2 Write integration tests for /api/metrics/ in core/tests.py (módulo único; ver docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md — mismo criterio que 11.x)
    - test_api_metrics_requires_privileged_profile: create Usuario user, verify HTTP 403
    - test_api_metrics_allows_administrador: create Administrador user, verify HTTP 200
    - test_api_metrics_returns_aggregated_data: create runs with different agents/states, verify response structure
    - **CRITICAL**: Use User.Profile.ADMINISTRADOR and User.Profile.USUARIO_IC constants in test assertions, NOT literal strings
    - _Requirements: 5.2, 5.3, 5.5_

  - [x] 12.3 Write integration tests for /api/admin/actions/ in core/tests.py (módulo único; ver docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md — mismo criterio que 11.x)
    - test_api_admin_actions_requires_administrador: create Usuario IC user, verify HTTP 403
    - test_api_admin_actions_returns_all_users_runs: create 2 users with runs, authenticate as Administrador, verify response contains runs from both users
    - test_api_admin_actions_filters_by_user_id: verify response only contains runs for specified user_id
    - **CRITICAL**: Use User.Profile.ADMINISTRADOR constant in test setup and assertions, NOT literal string
    - _Requirements: 10.2, 10.4, 10.5_

- [x] 13. Write integration tests for chat_view traceability
  - [x] 13.1 Write integration tests for /api/chat/ traceability in core/tests.py (módulo único; ver docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md — mismo criterio que 11.x)
    - test_chat_view_creates_workflow_run: POST valid query, verify WorkflowRun created with state='created'
    - test_chat_view_updates_run_on_success: mock n8n success response, verify WorkflowRun updated with state='completed' and agent_response
    - test_chat_view_updates_run_on_failure: mock n8n error, verify WorkflowRun updated with state='failed' and error_message
    - test_chat_view_records_execution_time: verify WorkflowRun.execution_time_ms > 0
    - test_chat_view_includes_metadata_in_response: mock n8n response with metadata, verify response JSON contains metadata fields
    - test_traceability_does_not_block_user_response: mock failure in TraceabilityManager.update_run(), verify user response still successful
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 14. Write model and template tests
  - [x] 14.1 Write model tests in core/tests.py (módulo único; ver docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md — mismo criterio que 11.x)
    - test_workflow_run_indexes_exist: inspect \_meta.indexes, verify all 4 indexes present
    - test_add_state_transition_updates_history: create WorkflowRun, call add_state_transition('running'), verify state_history and final_state updated
    - test_metric_event_defaults: create MetricEvent without value/metadata, verify defaults
    - _Requirements: 1.1, 2.9, 8.1_

  - [x] 14.2 Write template tests in core/tests.py (módulo único; ver docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md — mismo criterio que 11.x)
    - test_actions_page_requires_login: GET /actions/ unauthenticated, verify redirect to /login/
    - test_actions_page_renders_user_runs: create 3 runs, GET /actions/, verify 3 action cards rendered
    - test_actions_page_color_codes_states: create runs with different states, verify correct CSS classes
    - test_actions_page_paginates: create 25 runs, GET /actions/?page=1, verify only 20 runs shown and pagination controls present
    - _Requirements: 6.2, 6.3, 6.4, 6.6, 6.7_

- [x] 15. Final checkpoint - End-to-end validation
  - Verify complete flow: user makes query → WorkflowRun created → n8n called → WorkflowRun updated → metadata in response → action visible in /actions/ → metrics in /api/metrics/ (for admin), run all tests to ensure >80% coverage, report verification results point by point.

## Notes

- **Language**: Python (Django framework) - design explicitly uses Python/Django throughout
- **User.Profile Constants**: All profile comparisons MUST use `User.Profile.ADMINISTRADOR` and `User.Profile.USUARIO_IC` constants from the User model (spec usuarios-demo-perfiles-permisos), NOT literal strings like `'Administrador'` or `'Usuario IC'`. This applies to PermissionChecker service class, API views, and all tests.
- **No Property-Based Testing**: This spec uses unit tests and integration tests only, as it involves database operations, API endpoints, and infrastructure integration (no pure transformations with universal properties)
- **Transacción Separada**: TraceabilityManager uses `transaction.atomic()` for separate sync transactions - errors in traceability must NOT block user response
- **Test Coverage Goal**: >80% for service classes, 100% for API endpoints
- **CRITICAL - Permission Tests (12.2, 12.3)**: These tests validate that perfil Usuario cannot access metrics or other users' actions. They are mandatory for security validation and cannot be skipped.
- **Serial Execution**: Implementation must proceed serially, one subtask per Claude Code session, in numerical order. The Task Dependency Graph is provided as reference only, not for parallel execution.
- Each task references specific requirements for traceability
- Checkpoints report verification results point by point without interactive user input

## Task Dependency Graph

**Note**: This graph is provided as reference for understanding task dependencies only. Implementation must proceed serially, one subtask per Claude Code session, in numerical order (1.1 → 1.2 → 1.3 → 2 → 3.1 → 3.2 → ...).

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["1.3"] },
    { "id": 2, "tasks": ["3.1", "3.2", "3.3"] },
    { "id": 3, "tasks": ["5.1"] },
    { "id": 4, "tasks": ["5.2", "7.1", "7.2", "7.3"] },
    { "id": 5, "tasks": ["7.4", "9.1", "9.2", "9.3"] },
    { "id": 6, "tasks": ["9.4"] },
    { "id": 7, "tasks": ["9.5", "11.1", "11.2"] },
    { "id": 8, "tasks": ["12.1", "12.2", "12.3", "13.1"] },
    { "id": 9, "tasks": ["14.1", "14.2"] }
  ]
}
```
