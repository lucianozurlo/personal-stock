# Requirements Document

## Introduction

Este spec define el sistema de trazabilidad y métricas para Personal Stock MVP 1. Según el brief (sección 10) y security-permissions.md, la trazabilidad es OBLIGATORIA: toda ejecución de agente o workflow debe dejar registro completo. Sin trazabilidad, una tarea de implementación no se considera completa, aunque el código funcione.

El sistema debe registrar TODA ejecución de agente/workflow incluyendo: usuario que inició, fecha y hora, mensaje original, intención detectada, agente seleccionado, motivo de selección, datos usados, permisos aplicados, decisiones del sistema, respuesta generada, archivos cargados, aprobaciones, rechazos, correcciones, cambios de estado, resultado final y errores.

La trazabilidad debe ser visible de forma resumida para el usuario involucrado, más completa para Administrador y Usuario IC, y debe alimentar la página de acciones, el tablero de métricas y el historial de conversación.

Este spec depende de `home-chat-orchestrator-contract` (no hay qué trazar sin ejecución de orquestador). Los specs `rag-mails-dataset-permissions`, `trigger-comunicaciones-email` y `memoria-feedback-correcciones` dependen de este spec porque toda ejecución de agente debe quedar trazada.

## Glossary

- **Traceability_System**: Sistema que registra la trazabilidad completa de cada ejecución de agente o workflow
- **WorkflowRun**: Registro de trazabilidad de una ejecución completa de agente/workflow
- **MetricEvent**: Evento básico de métrica (contador, tiempo de ejecución, error)
- **Execution_State**: Estado actual de una ejecución (created, running, needs_input, waiting_human, pending_approval, approved, rejected, blocked_by_permissions, blocked_by_compliance, failed, cancelled, completed)
- **Agent_Execution**: Ejecución de un agente específico (RAG, Trigger Comunicaciones, Redactor CI, QA Editorial, Cumplimiento, etc.)
- **Orchestrator_Endpoint**: Endpoint `/api/chat/` definido en spec `home-chat-orchestrator-contract` que recibe queries del usuario y deriva a agentes
- **Actions_Page**: Página web que lista acciones del usuario actual con estado y detalle
- **Metrics_Dashboard**: Tablero de métricas visible solo para Administrador y Usuario IC
- **Trace_Metadata**: Metadatos de trazabilidad (agent_used, execution_time_ms, records_found) incluidos en Response_Payload del contrato
- **User_Profile**: Perfil del usuario (Administrador, Usuario IC, Heavy user, Macro, Usuario) definido en spec `usuarios-demo-perfiles-permisos`

## Requirements

### Requirement 1: Registrar trazabilidad de toda ejecución de agente

**User Story:** Como sistema, necesito registrar automáticamente la trazabilidad completa de cada ejecución de agente o workflow iniciada desde `/api/chat/`, para cumplir con la regla de trazabilidad obligatoria y permitir auditoría posterior.

#### Acceptance Criteria

1. WHEN a user submits a query to Orchestrator_Endpoint, THE Traceability_System SHALL create a WorkflowRun record with Execution_State "created" before calling the agent

2. THE WorkflowRun record SHALL include the field `user_id` storing the Django user.id of the authenticated user who initiated the execution

3. THE WorkflowRun record SHALL include the field `timestamp` storing the ISO 8601 datetime when the execution started

4. THE WorkflowRun record SHALL include the field `user_message` storing the original message text submitted by the user

5. THE WorkflowRun record SHALL include the field `detected_intention` storing the intention classification result (consulta_general, consulta_historial_mails, generar_plan_comunicacion, etc.)

6. THE WorkflowRun record SHALL include the field `selected_agent` storing the agent identifier that was selected to handle the request (rag-mails, trigger-comunicaciones, llm-base, etc.)

7. THE WorkflowRun record SHALL include the field `selection_reason` storing a brief explanation of why that agent was selected

8. THE WorkflowRun record SHALL include the field `permissions_applied` storing which permission checks were applied (e.g., "profile: Usuario, dataset filter: restricted recipients blocked")

9. THE WorkflowRun record SHALL include the field `agent_response` storing the final response text returned to the user

10. THE WorkflowRun record SHALL include the field `execution_time_ms` storing the total execution time in milliseconds

11. THE WorkflowRun record SHALL include the field `final_state` storing the Execution_State when the execution finishes

12. IF the agent execution encounters an error, THEN THE WorkflowRun record SHALL include the field `error_message` storing the error description

### Requirement 2: Soportar estados de ejecución

**User Story:** Como sistema, necesito actualizar el estado de cada ejecución a medida que progresa (created → running → completed/failed), para reflejar el ciclo de vida completo de la ejecución.

#### Acceptance Criteria

1. THE Traceability_System SHALL support the following Execution_State values: created, running, needs_input, waiting_human, pending_approval, approved, rejected, blocked_by_permissions, blocked_by_compliance, failed, cancelled, completed

2. WHEN a WorkflowRun is created, THE Traceability_System SHALL set initial Execution_State to "created"

3. WHEN the agent starts processing, THE Traceability_System SHALL update Execution_State to "running"

   > **MVP 1 limitation (see Decision 7 below):** This "running" transition is NOT exercised in MVP 1. Django registers the run in "created", calls n8n, and on response transitions directly to "completed"/"failed". The intermediate "running" state is prepared in the model for a future architecture where Django (not n8n) drives intention classification.

4. WHEN the agent completes successfully, THE Traceability_System SHALL update Execution_State to "completed"

5. WHEN the agent encounters an error, THE Traceability_System SHALL update Execution_State to "failed"

6. WHEN the agent is blocked by permissions, THE Traceability_System SHALL update Execution_State to "blocked_by_permissions"

7. WHEN the agent needs additional user input, THE Traceability_System SHALL update Execution_State to "needs_input"

8. WHEN the agent requires human approval, THE Traceability_System SHALL update Execution_State to "pending_approval"

9. THE Traceability_System SHALL store each state transition with timestamp in a state_history field or related table

10. THE Traceability_System SHALL expose the current Execution_State to the Actions_Page for display

### Requirement 3: Registrar decisiones del sistema

**User Story:** Como auditor, necesito revisar las decisiones que el sistema tomó durante una ejecución (qué agente eligió, por qué, qué permisos aplicó, qué datos usó), para validar que el comportamiento fue correcto.

#### Acceptance Criteria

1. THE WorkflowRun record SHALL include the field `system_decisions` storing a JSON object or text field with key decisions made during execution

2. THE system_decisions field SHALL include which agent was selected and why

3. THE system_decisions field SHALL include which permission checks passed or failed

4. THE system_decisions field SHALL include which data sources were queried (e.g., "historical dataset: 3 records matched after permission filter")

5. WHERE the agent is rag-mails, THE system_decisions field SHALL include how many records were found before and after applying permission filters

6. WHERE files were uploaded, THE system_decisions field SHALL include the file names and sizes

7. WHERE an approval was required, THE system_decisions field SHALL include who approved or rejected and when

8. WHERE a correction was applied by the user, THE system_decisions field SHALL include what was corrected

### Requirement 4: Exponer acciones del usuario actual

**User Story:** Como usuario autenticado, quiero ver un listado resumido de mis acciones (queries que envié, estado actual, fecha), para hacer seguimiento de lo que pedí al sistema.

#### Acceptance Criteria

1. THE Traceability_System SHALL provide an endpoint `/api/actions/` accessible to all authenticated users

2. WHEN a user requests `/api/actions/`, THE Traceability_System SHALL return only WorkflowRun records where `user_id` matches the authenticated user's ID

3. THE response SHALL include for each action: user_message (truncated to 100 characters), detected_intention, selected_agent, final_state, timestamp, execution_time_ms

4. THE response SHALL order actions by timestamp descending (most recent first)

5. THE response SHALL paginate results with 20 actions per page by default

6. THE Traceability_System SHALL return HTTP 401 if the user is not authenticated

### Requirement 5: Exponer métricas para perfiles privilegiados

**User Story:** Como usuario con perfil Administrador o Usuario IC, quiero acceder a un tablero de métricas que muestre estadísticas agregadas de uso del sistema, para monitorear el comportamiento y detectar problemas.

#### Acceptance Criteria

1. THE Traceability_System SHALL provide an endpoint `/api/metrics/` accessible only to users with User_Profile "Administrador" or "Usuario IC"

2. WHEN a user with User_Profile "Usuario", "Heavy user", or "Macro" requests `/api/metrics/`, THE Traceability_System SHALL return HTTP 403 Forbidden

3. THE `/api/metrics/` endpoint SHALL return aggregated metrics including: total executions, executions by agent, executions by state, average execution time per agent, error rate per agent

4. THE `/api/metrics/` endpoint SHALL accept optional query parameters `start_date` and `end_date` to filter metrics by date range

5. THE `/api/metrics/` endpoint SHALL return metrics in JSON format with clear field names (e.g., `total_executions`, `executions_by_agent`, `avg_execution_time_ms`)

6. THE Traceability_System SHALL compute metrics efficiently using database aggregation queries (not loading all records into memory)

### Requirement 6: Página de acciones con listado básico

**User Story:** Como usuario autenticado, quiero acceder a una página web que liste mis acciones de forma visual, para revisar el historial sin usar la API directamente.

#### Acceptance Criteria

1. THE Traceability_System SHALL provide a route `/actions/` that renders the Actions_Page template

2. THE Actions_Page SHALL display a table or card list with the user's recent actions

3. FOR each action in the Actions_Page, THE system SHALL display: truncated user_message, detected_intention, selected_agent, final_state (with color coding), timestamp (human-readable), execution_time_ms

4. THE Actions*Page SHALL use color coding for states: "completed" (green), "failed" or "blocked*\_" (red), "pending\_\_" or "waiting\_\*" (yellow), "running" or "needs_input" (blue)

5. WHEN the user clicks on an action, THE Actions_Page SHALL display full details including: full user_message, agent_response, system_decisions, permissions_applied, error_message (if any)

6. THE Actions_Page SHALL paginate results with navigation controls (previous/next page)

7. THE Actions_Page SHALL be accessible only to authenticated users (redirect to login if not authenticated)

### Requirement 7: Registrar trazabilidad en cada llamada a /api/chat/

**User Story:** Como sistema, necesito integrar el registro de trazabilidad en el endpoint `/api/chat/` de forma automática, para que no sea posible olvidar registrar una ejecución.

#### Acceptance Criteria

1. THE Orchestrator_Endpoint `/api/chat/` SHALL call Traceability_System to create a WorkflowRun record at the start of each request

2. WHEN the agent (n8n) returns a response, THE Orchestrator_Endpoint SHALL update the WorkflowRun record with the actual `selected_agent` (from `metadata.agent_used`), the final state, and the response, transitioning the run from "created" to "completed" or "failed"

   > **MVP 1 limitation (see Decision 7 below):** Django does NOT populate `detected_intention`, `selection_reason` or `permissions_applied`, nor does it transition through the "running" state, because intention classification and agent selection are performed by n8n (decided in the closed spec `home-chat-orchestrator-contract`), not by Django. Django does not hold that data "before calling the agent". The `WorkflowRun` fields and the `TraceabilityManager.update_run_agent_selection()` method exist and are unit-tested, but remain **prepared and not populated** in MVP 1. They would only be populated if a future n8n contract exposes `detected_intention` / `selection_reason`.

3. THE Orchestrator_Endpoint SHALL update the WorkflowRun record with the agent response and final state after the agent returns

4. THE Orchestrator_Endpoint SHALL update the WorkflowRun record with error information if the agent call fails

5. THE Orchestrator_Endpoint SHALL complete the WorkflowRun update even if the agent response generation succeeds but the final state update fails (ensure traceability even in partial failure scenarios)

6. THE Traceability_System SHALL execute all database writes in a separate transaction (synchronous) to ensure traceability is persisted even if subsequent processing fails, while avoiding blocking the agent response to the user

### Requirement 8: Registrar métricas básicas

**User Story:** Como sistema, necesito registrar eventos de métrica simples (contadores, tiempos, errores) además de la trazabilidad completa, para poder generar reportes agregados sin procesar todos los WorkflowRun.

#### Acceptance Criteria

1. THE Traceability_System SHALL provide a MetricEvent model with fields: event_type, agent, timestamp, value, metadata

2. WHEN an agent execution completes, THE Traceability_System SHALL create a MetricEvent with event_type "agent_execution" and value set to execution_time_ms

3. WHEN an agent execution fails, THE Traceability_System SHALL create a MetricEvent with event_type "agent_error" and metadata containing the error type

4. WHEN a permission check blocks an execution, THE Traceability_System SHALL create a MetricEvent with event_type "permission_blocked" and metadata containing the profile and restriction applied

5. THE MetricEvent records SHALL be stored in a separate table from WorkflowRun to allow independent retention policies

6. THE `/api/metrics/` endpoint SHALL aggregate MetricEvent records (not WorkflowRun) for performance

### Requirement 9: Incluir metadata de trazabilidad en Response_Payload

**User Story:** Como frontend, necesito recibir metadata de trazabilidad (agent_used, execution_time_ms, records_found) en cada respuesta del orquestador, para mostrar información de contexto al usuario.

#### Acceptance Criteria

1. THE Orchestrator_Endpoint SHALL include a `metadata` object in the Response_Payload as defined in spec `home-chat-orchestrator-contract`

2. THE metadata object SHALL include the field `agent_used` with the selected agent identifier

3. THE metadata object SHALL include the field `execution_time_ms` with the total execution time in milliseconds

4. THE metadata object SHALL include the field `records_found` with the number of records returned by the agent (null if not applicable)

5. THE metadata object SHALL conform to the Trace_Metadata structure defined in the Glossary of spec `home-chat-orchestrator-contract`

6. THE Orchestrator_Endpoint SHALL populate the metadata object from the WorkflowRun record after the agent completes

### Requirement 10: Permitir consulta de trazabilidad por administradores

**User Story:** Como usuario con perfil Administrador, quiero consultar la trazabilidad de cualquier usuario del sistema, para auditar comportamiento, detectar problemas o revisar casos de soporte.

#### Acceptance Criteria

1. THE Traceability_System SHALL provide an endpoint `/api/admin/actions/` accessible only to users with User_Profile "Administrador"

2. WHEN a user with User_Profile other than "Administrador" requests `/api/admin/actions/`, THE Traceability_System SHALL return HTTP 403 Forbidden

3. THE `/api/admin/actions/` endpoint SHALL accept an optional query parameter `user_id` to filter actions by a specific user

4. WHERE `user_id` is not provided, THE `/api/admin/actions/` endpoint SHALL return actions from all users

5. THE response format SHALL match the format of `/api/actions/` (same fields, same pagination)

6. THE `/api/admin/actions/` endpoint SHALL include additional fields not visible in `/api/actions/`: user_email, user_name, permissions_applied, system_decisions

## Conflicts and Decisions

### Conflict 1: WorkflowRun vs múltiples tablas relacionadas

**Conflicto detectado:** No está claro si WorkflowRun debe ser un solo modelo Django con muchos campos JSON, o si debe normalizarse en múltiples tablas relacionadas (WorkflowRun, StateTransition, SystemDecision, FileUpload, etc.).

**Resolución:** Usar un modelo WorkflowRun con campos estructurados para datos clave (user_id, timestamp, detected_intention, selected_agent, final_state) y campos JSON/TextField para datos variables (system_decisions, permissions_applied, state_history). Esto permite flexibilidad sin complejidad prematura. Si en MVP posterior se necesita consultar eficientemente dentro de system_decisions, se puede normalizar entonces.

**Documentación:** Queda documentado en Requirement 1 (campos estructurados) y Requirement 3 (system_decisions como JSON).

---

### Conflict 2: Registro síncrono vs asíncrono

**Conflicto detectado:** ¿El registro de trazabilidad debe bloquear la respuesta al usuario o debe ejecutarse en background?

**Resolución:** El registro de trazabilidad debe ejecutarse de forma que NO bloquee la respuesta al usuario. Requirement 7 AC6 establece: "execute all database writes in a separate transaction". En MVP 1, usar transacción separada SÍNCRONA simple (NO Celery, NO threads, NO async). La trazabilidad se escribe en el mismo request pero en transacción separada para que un fallo de trazabilidad no tire la respuesta al usuario. En MVP posterior, si el volumen crece o se necesita desacoplamiento completo, migrar a cola de tareas (Celery, RQ).

**Documentación:** Queda documentado en Requirement 7 AC6.

---

### Conflict 3: Retención de datos de trazabilidad

**Conflicto detectado:** No está claro cuánto tiempo se deben retener los registros de WorkflowRun y MetricEvent, ni si hay diferencia entre ambos.

**Resolución:** En MVP 1, NO implementar política de retención automática (se retiene todo indefinidamente). Documentar en spec `documentacion-local-y-limites-mvp` que la retención es una limitación conocida de MVP 1 y debe implementarse en MVP posterior. Requirement 8 AC5 menciona "independent retention policies" para dejar la puerta abierta.

**Documentación:** Queda documentado en Requirement 8 AC5 (tablas separadas para permitir políticas diferentes en el futuro) y debe mencionarse como limitación en spec 9.

---

### Conflict 4: Manejo de errores de n8n (sin mock)

**Conflicto detectado:** ¿Cómo se traza una ejecución cuando n8n no está disponible o falla?

**Resolución:** Según el spec `home-chat-orchestrator-contract` (Conflict 4), NO hay mock de n8n en el proyecto. Cuando n8n no está disponible o falla, se devuelve error claro al usuario y se traza como cualquier otro error: `final_state="failed"` con `error_message` descriptivo. No existen ejecuciones simuladas en este proyecto.

**Impacto:** No se necesita campo `is_simulated` en WorkflowRun. Los errores de n8n se trazan igual que cualquier otro error del sistema.

**Documentación:** Queda documentado en este Conflict y en la estructura del modelo WorkflowRun en Notes (sin campo `is_simulated`).

---

### Conflict 5: Visibilidad de datos sensibles en trazabilidad

**Conflicto detectado:** ¿Los campos de trazabilidad (user_message, agent_response, system_decisions) pueden contener datos sensibles (PII, información restringida del dataset)?

**Resolución:** SÍ, los campos de trazabilidad pueden contener datos sensibles. La protección se aplica en dos niveles:

1. **Permisos de lectura**: Solo el usuario que inició la acción puede ver su trazabilidad completa (Requirement 4). Administrador puede ver trazabilidad de todos (Requirement 10).
2. **No cambiar el comportamiento de filtrado**: La trazabilidad NO reintroduce contenido restringido. Si el usuario con perfil Usuario hizo una consulta y el sistema bloqueó contenido restringido, el campo agent_response registra la respuesta bloqueada ("Encontré información relacionada... no tengo permiso..."), NO el contenido bloqueado.

**Documentación:** Queda documentado en Requirement 4 AC2 (solo el usuario ve su trazabilidad) y Requirement 10 (solo Administrador ve trazabilidad de todos).

---

### Conflict 6: Estructura de la página de acciones (MVP 1 simple)

**Conflicto detectado:** No está claro si la página de acciones debe ser una SPA con filtros avanzados o un template Django simple.

**Resolución:** En MVP 1, la página de acciones es un template Django simple con tabla/cards y paginación básica. NO es SPA, NO tiene filtros complejos (solo paginación). Si en MVP posterior se requiere búsqueda/filtrado avanzado, se puede evolucionar a SPA. Requirement 6 define solo funcionalidad básica.

**Documentación:** Queda documentado en Requirement 6 (template simple, paginación básica, detalle expandible).

---

### Conflict 7: Clasificación de intención y estado "running" — Django vs n8n

**Conflicto detectado:** Los Requirements 7 AC2, 2.3 y (por extensión) 2.7 asumen que Django clasifica la intención, selecciona el agente y transiciona a estado `running` **antes de llamar al agente**. En la arquitectura real, decidida en el spec ya cerrado `home-chat-orchestrator-contract`, esa clasificación la hace **n8n externamente**. El contrato de respuesta (Response_Payload) solo expone `metadata: {agent_used, execution_time_ms, records_found}`, sin `detected_intention` ni `selection_reason`. Django no tiene esos datos antes de llamar a n8n.

**Efecto observado en el código (verificado en tarea 13.1, devolución 127):**

- `TraceabilityManager.update_run_agent_selection()` existe y tiene unit test, pero **nunca se invoca desde `chat_view`**.
- `final_state` no transiciona por `running` (va de `created` directo a `completed`/`failed`).
- `detected_intention`, `selection_reason` y `permissions_applied` quedan vacíos.
- `selected_agent` **sí** se puebla, a posteriori, desde `metadata.agent_used`.

**Resolución (aprobada, MVP 1):** Documentar que en MVP 1 el estado `running` y los campos `detected_intention` / `selection_reason` / `permissions_applied` quedan **preparados en el modelo pero NO poblados**. El modelo `WorkflowRun` y el método `update_run_agent_selection()` existen para MVP posterior. Poblarlos requeriría extender el contrato de n8n para que exponga `detected_intention` / `selection_reason`, lo cual queda **fuera del alcance de MVP 1**. `selected_agent` sí se puebla desde `metadata.agent_used`. Esta decisión NO reabre `home-chat-orchestrator-contract`.

**Coherencia:** Alineado con `product.md` ("Si una parte no puede completarse en MVP 1, queda marcada como preparada para MVP posterior — nunca se omite en silencio") y con `rules.md` (no reabrir specs cerrados).

**Documentación:** Queda documentado en Requirement 7 AC2, Requirement 2.3 (notas de limitación MVP 1) y en la sección Testing Strategy / Data Models de `design.md`.

## Notes

### Dependencias de specs

- **home-chat-orchestrator-contract**: Este spec asume que el endpoint `/api/chat/` ya existe y que el contrato de Response_Payload incluye campo `metadata` con `agent_used`, `execution_time_ms`, `records_found`.
- **usuarios-demo-perfiles-permisos**: Este spec asume que el modelo User tiene campo `perfil` y que los perfiles "Administrador" y "Usuario IC" están definidos.
- **Specs dependientes**: Los specs `rag-mails-dataset-permissions`, `trigger-comunicaciones-email` y `memoria-feedback-correcciones` dependen de este spec porque deben registrar trazabilidad obligatoria.

### Campos sugeridos para WorkflowRun (modelo Django)

```python
class WorkflowRun(models.Model):
    # Identificación
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation_id = models.CharField(max_length=50)  # del Request_Payload

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    execution_time_ms = models.IntegerField(null=True)

    # Input
    user_message = models.TextField()
    detected_intention = models.CharField(max_length=100)

    # Agent selection
    selected_agent = models.CharField(max_length=100)
    selection_reason = models.TextField()

    # Permissions and decisions
    permissions_applied = models.TextField()  # JSON o texto estructurado
    system_decisions = models.JSONField()

    # Output
    agent_response = models.TextField()
    error_message = models.TextField(null=True, blank=True)

    # State
    final_state = models.CharField(
        max_length=50,
        choices=[
            ('created', 'Created'),
            ('running', 'Running'),
            ('needs_input', 'Needs Input'),
            ('waiting_human', 'Waiting Human'),
            ('pending_approval', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('blocked_by_permissions', 'Blocked by Permissions'),
            ('blocked_by_compliance', 'Blocked by Compliance'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
            ('completed', 'Completed'),
        ]
    )
    state_history = models.JSONField(default=list)  # lista de {state, timestamp}
```

### Campos sugeridos para MetricEvent

```python
class MetricEvent(models.Model):
    event_type = models.CharField(max_length=50)  # agent_execution, agent_error, permission_blocked
    agent = models.CharField(max_length=100, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField(null=True)  # ej: execution_time_ms
    metadata = models.JSONField(default=dict)
```

### Ejemplo de system_decisions JSON

```json
{
  "agent_selection": {
    "reason": "User query matches 'consulta_historial_mails' intention pattern",
    "candidates": ["rag-mails", "llm-base"],
    "selected": "rag-mails"
  },
  "permission_checks": {
    "profile": "Usuario",
    "restrictions_applied": ["dataset: blocked recipients containing 'macro'"],
    "records_before_filter": 5,
    "records_after_filter": 2
  },
  "data_sources": [
    { "source": "relevamiento_enriquecido.json", "records_matched": 2 }
  ]
}
```

### Integración con /api/chat/

El endpoint `/api/chat/` (definido en spec 3) debe modificarse para:

1. Crear WorkflowRun al inicio con state="created"
2. Actualizar state="running" antes de llamar al agente
3. Actualizar system_decisions con decisiones de selección de agente y permisos
4. Actualizar agent_response y final_state al recibir respuesta del agente
5. Actualizar error_message y final_state="failed" si el agente falla
6. Incluir metadata en Response_Payload poblado desde WorkflowRun

### Performance

- Los registros de WorkflowRun crecen indefinidamente en MVP 1 (sin política de retención).
- Con 100 usuarios demo y uso moderado, se estima <10k registros en MVP 1 (manejable sin optimización).
- Si en MVP posterior el volumen crece, considerar: particionamiento por fecha, archivado de registros viejos, índices en user_id + timestamp.

### Información contextual

- Brief sección 9: estados mínimos (created, running, needs_input, waiting_human, pending_approval, approved, rejected, blocked_by_permissions, blocked_by_compliance, failed, cancelled, completed)
- Brief sección 10: trazabilidad obligatoria (usuario, fecha, mensaje, intención, agente, permisos, decisiones, respuesta, errores)
- security-permissions.md: "Sin trazabilidad, una tarea de implementación no se considera completa"
- spec home-chat-orchestrator-contract (Conflict 4): NO hay mock de n8n; los errores se trazan con final_state="failed"
