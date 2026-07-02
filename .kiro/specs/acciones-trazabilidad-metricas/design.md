# Design Document

## Overview

Este diseño implementa el sistema de trazabilidad y métricas obligatorio para Personal Stock MVP 1. Según `security-permissions.md`, toda ejecución de agente o workflow debe dejar registro completo. Sin trazabilidad, una tarea de implementación no se considera completa.

El sistema registra automáticamente TODA ejecución iniciada desde `/api/chat/` mediante dos modelos Django:

- **WorkflowRun**: Registro completo de trazabilidad (usuario, timestamps, input, decisiones del sistema, permisos, output, estado, errores)
- **MetricEvent**: Eventos de métrica agregables (contadores, tiempos de ejecución, errores)

La integración con `/api/chat/` es **transparente y obligatoria**: el endpoint crea y actualiza WorkflowRun automáticamente en cada request mediante transacción separada síncrona (NO async, NO Celery en MVP 1).

El sistema expone:

- `GET /api/actions/` — lista acciones del usuario actual (todos los perfiles)
- `GET /api/metrics/` — métricas agregadas (solo Administrador y Usuario IC)
- `GET /api/admin/actions/` — lista acciones de cualquier usuario (solo Administrador)
- `GET /actions/` — página web con listado visual de acciones

### Design Goals

1. **Trazabilidad obligatoria**: Ninguna ejecución puede escapar del registro
2. **Transacción separada**: Los errores de trazabilidad no deben afectar la respuesta al usuario
3. **Performance**: Queries eficientes usando agregación SQL, índices en campos de búsqueda
4. **Permisos estrictos**: Solo el usuario ve su trazabilidad; Administrador ve todas
5. **Escalabilidad MVP 1**: Diseño simple que soporte ~10k registros sin optimización compleja

## Architecture

### Component Interaction

```
┌─────────────┐
│  Frontend   │
│  (home.html)│
└──────┬──────┘
       │ POST /api/chat/
       ↓
```

┌─────────────────────────────────────────────────┐
│ chat_view (core/views.py) │
│ │
│ 1. Parse request body │
│ 2. Validate payload │
│ 3. ┌─────────────────────────────────────┐ │
│ │ TraceabilityManager.create_run() │ │
│ │ → WorkflowRun(state="created") │ │
│ └─────────────────────────────────────┘ │
│ 4. Call n8n orchestrator │
│ 5. ┌─────────────────────────────────────┐ │
│ │ TraceabilityManager.update_run() │ │
│ │ → state="completed"/"failed" │ │
│ │ → agent_response, error_message │ │
│ └─────────────────────────────────────┘ │
│ 6. Return response to frontend │
└─────────────────────────────────────────────────┘
│
↓
┌─────────────────────────────────────────────────┐
│ Django ORM │
│ ┌──────────────┐ ┌────────────────┐ │
│ │ WorkflowRun │ │ MetricEvent │ │
│ │ (main trace)│ │ (aggregated) │ │
│ └──────────────┘ └────────────────┘ │
└─────────────────────────────────────────────────┘

### Layered Architecture

```
┌──────────────────────────────────────────────────┐
│             Presentation Layer                   │
│  - /api/actions/ (REST endpoint)                 │
│  - /api/metrics/ (REST endpoint)                 │
│  - /api/admin/actions/ (REST endpoint)           │
│  - /actions/ (Django template view)              │
└──────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────┐
│             Business Logic Layer                 │
│  - TraceabilityManager (service class)           │
│  - MetricsAggregator (service class)             │
│  - PermissionChecker (access control)            │
└──────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────┐
│                Data Layer                        │
│  - WorkflowRun model                             │
│  - MetricEvent model                             │
│  - User model (from usuarios-demo-perfiles)      │
└──────────────────────────────────────────────────┘
```

### Integration Points

1. **chat_view (core/views.py)**: Modificar para registrar trazabilidad automáticamente
2. **Response payload**: Incluir `metadata` object según contrato de `home-chat-orchestrator-contract`
3. **Session data**: Usar `request.user` para identificar usuario autenticado
4. **State transitions**: Actualizar WorkflowRun.state y WorkflowRun.state_history durante ejecución

## Components and Interfaces

### 1. TraceabilityManager (Service Class)

**Purpose**: Centraliza la lógica de creación y actualización de WorkflowRun. Asegura que todos los campos requeridos se registran correctamente y que las transacciones se manejan de forma segura.

**Public Interface**:

```python
class TraceabilityManager:
    @staticmethod
    def create_run(
        user: User,
        conversation_id: str,
        user_message: str,
        agent_type: str
    ) -> WorkflowRun:
        """
        Crea un nuevo WorkflowRun con state="created".

        Ejecuta en transacción separada para que un fallo de trazabilidad
        no afecte la respuesta al usuario.
        """
        pass

    @staticmethod
    def update_run_agent_selection(
        run_id: int,
        detected_intention: str,
        selected_agent: str,
        selection_reason: str,
        permissions_applied: dict
    ) -> None:
        """
        Actualiza el WorkflowRun después de seleccionar agente.
        state: "created" → "running"
        """
        pass

    @staticmethod
    def complete_run(
        run_id: int,
        agent_response: str,
        execution_time_ms: int,
        metadata: dict
    ) -> None:
        """
        Marca el WorkflowRun como completado.
        state: "running" → "completed"
        """
        pass

    @staticmethod
    def fail_run(
        run_id: int,
        error_message: str,
        execution_time_ms: int
    ) -> None:
        """
        Marca el WorkflowRun como fallido.
        state: any → "failed"
        """
        pass
```

**Implementation Notes**:

- Usa `transaction.atomic()` con `using='default'` para transacción separada
- Registra errores de trazabilidad en logs pero NO los propaga al caller
- Cada método actualiza `WorkflowRun.updated_at` automáticamente (auto_now=True)
- Agrega entradas a `state_history` en cada cambio de estado

**State Transition Rules**:

```
created → running → completed
created → running → failed
created → failed (si falla antes de llamar agente)
running → blocked_by_permissions (si permisos fallan)
running → needs_input (si agente requiere input adicional)
running → pending_approval (si agente requiere aprobación)
```

> **⚠️ Limitación MVP 1 (Decision 7 en requirements.md):** Las transiciones que pasan por
> `running` describen el diseño objetivo, pero **NO se ejercitan en MVP 1**. En la arquitectura
> real (spec cerrado `home-chat-orchestrator-contract`), la clasificación de intención y la
> selección de agente las hace **n8n**, no Django. Por lo tanto:
>
> - `chat_view` transiciona `created → completed` o `created → failed` directamente (nunca por `running`).
> - `TraceabilityManager.update_run_agent_selection()` existe y está unit-testeado, pero **no se
>   invoca desde `chat_view`** (queda preparado para MVP posterior).
> - Los campos `detected_intention`, `selection_reason` y `permissions_applied` quedan **preparados
>   pero no poblados**; solo se poblarían si un contrato futuro de n8n los expone.
> - `selected_agent` **sí** se puebla a posteriori desde `metadata.agent_used` de la respuesta de n8n.

### 2. MetricsAggregator (Service Class)

**Purpose**: Genera métricas agregadas a partir de WorkflowRun y MetricEvent para el endpoint `/api/metrics/`.

**Public Interface**:

```python
class MetricsAggregator:
    @staticmethod
    def get_summary_metrics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        Retorna métricas agregadas:
        - total_executions
        - executions_by_agent
        - executions_by_state
        - avg_execution_time_ms (por agente)
        - error_rate (por agente)
        """
        pass

    @staticmethod
    def record_metric_event(
        event_type: str,
        agent: str,
        value: Optional[int] = None,
        metadata: Optional[dict] = None
    ) -> None:
        """
        Crea un MetricEvent para agregación futura.
        """
        pass
```

**Implementation Notes**:

- Usa Django ORM aggregation: `Count()`, `Avg()`, `annotate()`, `values()`
- Filtra por fecha usando `created_at__gte` y `created_at__lte`
- Calcula error_rate como `COUNT(final_state='failed') / COUNT(*)`
- Todas las queries se ejecutan en una sola transacción de lectura

### 3. PermissionChecker (Service Class)

**Purpose**: Verifica permisos de acceso a endpoints de trazabilidad según perfil del usuario. Usa las constantes de TextChoices del modelo User (spec 2: usuarios-demo-perfiles-permisos) en lugar de strings literales para evitar fragilidad por typos.

**Public Interface**:

```python
class PermissionChecker:
    @staticmethod
    def can_access_metrics(user) -> bool:
        """
        Verifica si el usuario puede acceder a /api/metrics/.
        Solo perfiles Administrador y Usuario IC tienen acceso.

        Usa User.Profile.ADMINISTRADOR y User.Profile.USUARIO_IC
        del modelo User (spec usuarios-demo-perfiles-permisos).
        """
        from core.models import User
        return user.perfil in [
            User.Profile.ADMINISTRADOR,
            User.Profile.USUARIO_IC
        ]

    @staticmethod
    def can_access_admin_actions(user) -> bool:
        """
        Verifica si el usuario puede acceder a /api/admin/actions/.
        Solo perfil Administrador tiene acceso.

        Usa User.Profile.ADMINISTRADOR del modelo User.
        """
        from core.models import User
        return user.perfil == User.Profile.ADMINISTRADOR

    @staticmethod
    def get_user_runs_queryset(user):
        """
        Retorna queryset de WorkflowRun filtrado por usuario.
        Para uso en /api/actions/.
        """
        from core.models import WorkflowRun
        return WorkflowRun.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def get_all_runs_queryset(user_id: Optional[int] = None):
        """
        Retorna queryset de WorkflowRun de todos los usuarios (admin only).
        Opcionalmente filtrado por user_id específico.
        Para uso en /api/admin/actions/.
        """
        from core.models import WorkflowRun
        queryset = WorkflowRun.objects.all().order_by('-created_at')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset
```

**Implementation Notes**:

- **CRÍTICO**: Usa `User.Profile.ADMINISTRADOR`, `User.Profile.USUARIO_IC` (constantes de TextChoices definidas en spec usuarios-demo-perfiles-permisos) en lugar de strings literales `'Administrador'`, `'Usuario IC'`
- Esto evita errores por typos y hace el código refactor-safe
- Si el modelo User no expone estas constantes públicamente, deben agregarse al modelo en spec 2
- Todas las comparaciones de perfil en el sistema deben usar estas constantes

### 3. API Endpoints

#### 3.1 GET /api/actions/

**Purpose**: Lista acciones del usuario autenticado actual.

**Request**:

- Method: GET
- Auth: Required (Django session authentication)
- Query params:
  - `page` (optional, default=1): número de página
  - `page_size` (optional, default=20): registros por página

**Response** (200 OK):

```json
{
  "count": 42,
  "next": "/api/actions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 123,
      "user_message": "¿Qué comunicaciones recientes hay sobre beneficios?",
      "detected_intention": "consulta_historial_mails",
      "selected_agent": "rag-mails",
      "final_state": "completed",
      "timestamp": "2026-04-17T14:32:15.123Z",
      "execution_time_ms": 450
    }
  ]
}
```

**Permissions**: Todos los usuarios autenticados pueden ver sus propias acciones.

**Pagination**: Django REST Framework `PageNumberPagination` con 20 items por página.

#### 3.2 GET /api/metrics/

**Purpose**: Retorna métricas agregadas para perfiles Administrador y Usuario IC.

**Request**:

- Method: GET
- Auth: Required (Django session authentication)
- Permissions: Solo `perfil IN [User.Profile.ADMINISTRADOR, User.Profile.USUARIO_IC]` (constantes del modelo User)
- Query params:
  - `start_date` (optional, ISO 8601): fecha inicio filtro
  - `end_date` (optional, ISO 8601): fecha fin filtro

**Response** (200 OK):

```json
{
  "total_executions": 150,
  "executions_by_agent": {
    "rag-mails": 80,
    "trigger-comunicaciones": 45,
    "llm-base": 25
  },
  "executions_by_state": {
    "completed": 135,
    "failed": 10,
    "blocked_by_permissions": 5
  },
  "avg_execution_time_ms": {
    "rag-mails": 450,
    "trigger-comunicaciones": 1200,
    "llm-base": 350
  },
  "error_rate": {
    "rag-mails": 0.05,
    "trigger-comunicaciones": 0.11,
    "llm-base": 0.02
  }
}
```

**Response** (403 Forbidden):

```json
{
  "error": "No tiene permisos para acceder a las métricas"
}
```

**Permissions**: Solo usuarios con `perfil=User.Profile.ADMINISTRADOR` o `perfil=User.Profile.USUARIO_IC` (constantes del modelo User).

#### 3.3 GET /api/admin/actions/

**Purpose**: Lista acciones de cualquier usuario (solo Administrador).

**Request**:

- Method: GET
- Auth: Required (Django session authentication)
- Permissions: Solo `perfil=User.Profile.ADMINISTRADOR` (constante del modelo User)
- Query params:
  - `user_id` (optional): filtrar por usuario específico
  - `page` (optional, default=1): número de página
  - `page_size` (optional, default=20): registros por página

**Response** (200 OK):

```json
{
  "count": 500,
  "next": "/api/admin/actions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 123,
      "user_id": 42,
      "user_email": "comustock.ci@gmail.com",
      "user_name": "Luciano Zurlo",
      "user_message": "¿Qué comunicaciones recientes hay sobre beneficios?",
      "detected_intention": "consulta_historial_mails",
      "selected_agent": "rag-mails",
      "permissions_applied": "profile: Administrador, no restrictions",
      "system_decisions": { "agent_selection": { ... } },
      "final_state": "completed",
      "timestamp": "2026-04-17T14:32:15.123Z",
      "execution_time_ms": 450
    }
  ]
}
```

**Response** (403 Forbidden):

```json
{
  "error": "Solo los administradores pueden acceder a esta información"
}
```

**Permissions**: Solo usuarios con `perfil=User.Profile.ADMINISTRADOR` (constante del modelo User).

#### 3.4 GET /actions/

**Purpose**: Página web Django que muestra listado visual de acciones del usuario actual.

**Request**:

- Method: GET
- Auth: Required (Django login_required decorator)
- Query params:
  - `page` (optional, default=1): número de página

**Response**: Renderiza template `actions.html` con contexto:

```python
{
    'actions': WorkflowRun.objects.filter(user=request.user).order_by('-created_at'),
    'page_obj': paginator.page(page_number),
    'user': request.user,
}
```

**Template Structure** (actions.html):

- Header con logo y nombre de usuario
- Tabla/cards con acciones recientes
- Color coding por estado (verde, rojo, amarillo, azul)
- Modal o expandible para mostrar detalles completos al hacer click
- Controles de paginación (anterior/siguiente)

**Permissions**: Solo usuarios autenticados. Redirige a `/login/` si no autenticado.

### 4. Django Template (actions.html)

**Location**: `~/Desktop/PS-edit/templates/actions.html`

**Structure**:

```html
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <title>Mis Acciones - Personal Stock</title>
    <link rel="stylesheet" href="{% static 'css/actions.css' %}" />
  </head>
  <body>
    <header>
      <img
        src="{% static 'img/personal-stock-logo.svg' %}"
        alt="Personal Stock"
      />
      <span>{{ user.get_full_name }}</span>
    </header>

    <main>
      <h1>Mis Acciones</h1>

      <div class="actions-list">
        {% for action in page_obj %}
        <div class="action-card state-{{ action.final_state }}">
          <div class="action-header">
            <span class="timestamp"
              >{{ action.created_at|date:"d/m/Y H:i" }}</span
            >
            <span class="state-badge"
              >{{ action.get_final_state_display }}</span
            >
          </div>
          <div class="action-body">
            <p class="message">{{ action.user_message|truncatewords:20 }}</p>
            <p class="meta">
              <strong>Agente:</strong> {{ action.selected_agent }}
              <strong>Tiempo:</strong> {{ action.execution_time_ms }}ms
            </p>
          </div>
          <button onclick="showDetails({{ action.id }})">Ver detalles</button>
        </div>
        {% empty %}
        <p>No hay acciones registradas todavía.</p>
        {% endfor %}
      </div>

      <div class="pagination">
        {% if page_obj.has_previous %}
        <a href="?page={{ page_obj.previous_page_number }}">← Anterior</a>
        {% endif %}
        <span
          >Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages
          }}</span
        >
        {% if page_obj.has_next %}
        <a href="?page={{ page_obj.next_page_number }}">Siguiente →</a>
        {% endif %}
      </div>
    </main>

    <div id="detailsModal" class="modal">
      <!-- Modal content populated via JavaScript -->
    </div>

    <script src="{% static 'js/actions.js' %}"></script>
  </body>
</html>
```

## Data Models

### 1. WorkflowRun Model

**Purpose**: Registro completo de trazabilidad de una ejecución de agente/workflow.

**Fields**:

```python
class WorkflowRun(models.Model):
    """
    Registro de trazabilidad completo de una ejecución de agente o workflow.
    """

    class ExecutionState(models.TextChoices):
        CREATED = 'created', 'Creado'
        RUNNING = 'running', 'Ejecutando'
        NEEDS_INPUT = 'needs_input', 'Necesita Input'
        WAITING_HUMAN = 'waiting_human', 'Esperando Humano'
        PENDING_APPROVAL = 'pending_approval', 'Pendiente de Aprobación'
        APPROVED = 'approved', 'Aprobado'
        REJECTED = 'rejected', 'Rechazado'
        BLOCKED_BY_PERMISSIONS = 'blocked_by_permissions', 'Bloqueado por Permisos'
        BLOCKED_BY_COMPLIANCE = 'blocked_by_compliance', 'Bloqueado por Compliance'
        FAILED = 'failed', 'Fallido'
        CANCELLED = 'cancelled', 'Cancelado'
        COMPLETED = 'completed', 'Completado'

    # Identificación
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='workflow_runs',
        verbose_name='Usuario'
    )
    conversation_id = models.CharField(
        max_length=50,
        verbose_name='ID de conversación'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )
    execution_time_ms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Tiempo de ejecución (ms)'
    )

    # Input
    user_message = models.TextField(
        verbose_name='Mensaje del usuario'
    )
    detected_intention = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Intención detectada'
    )

    # Agent selection
    selected_agent = models.CharField(
        max_length=100,
        verbose_name='Agente seleccionado'
    )
    selection_reason = models.TextField(
        blank=True,
        verbose_name='Motivo de selección'
    )

    # Permissions and decisions
    permissions_applied = models.TextField(
        blank=True,
        verbose_name='Permisos aplicados',
        help_text='Descripción textual de permisos aplicados'
    )
    system_decisions = models.JSONField(
        default=dict,
        verbose_name='Decisiones del sistema',
        help_text='JSON con decisiones clave: agent_selection, permission_checks, data_sources'
    )

    # Output
    agent_response = models.TextField(
        blank=True,
        verbose_name='Respuesta del agente'
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='Mensaje de error'
    )

    # State
    final_state = models.CharField(
        max_length=50,
        choices=ExecutionState.choices,
        default=ExecutionState.CREATED,
        verbose_name='Estado final'
    )
    state_history = models.JSONField(
        default=list,
        verbose_name='Historial de estados',
        help_text='Lista de {state, timestamp} con transiciones de estado'
    )

    class Meta:
        verbose_name = 'Ejecución de Workflow'
        verbose_name_plural = 'Ejecuciones de Workflow'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['final_state']),
            models.Index(fields=['selected_agent']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Run #{self.id} - {self.user.email} - {self.final_state}"

    def add_state_transition(self, new_state: str) -> None:
        """Agrega una transición de estado al historial."""
        self.state_history.append({
            'state': new_state,
            'timestamp': timezone.now().isoformat()
        })
        self.final_state = new_state
```

**Indexes Rationale**:

- `(user, -created_at)`: Para `/api/actions/` que filtra por usuario y ordena por fecha descendente
- `final_state`: Para métricas por estado
- `selected_agent`: Para métricas por agente
- `created_at`: Para filtrado por rango de fechas en métricas

**JSON Field Schemas**:

**system_decisions** (example):

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

**state_history** (example):

```json
[
  { "state": "created", "timestamp": "2026-04-17T14:32:15.123Z" },
  { "state": "running", "timestamp": "2026-04-17T14:32:15.456Z" },
  { "state": "completed", "timestamp": "2026-04-17T14:32:15.890Z" }
]
```

### 2. MetricEvent Model

**Purpose**: Eventos de métrica para agregación eficiente sin procesar todos los WorkflowRun.

**Fields**:

```python
class MetricEvent(models.Model):
    """
    Evento de métrica individual para agregación.
    Separado de WorkflowRun para permitir políticas de retención diferentes.
    """

    class EventType(models.TextChoices):
        AGENT_EXECUTION = 'agent_execution', 'Ejecución de Agente'
        AGENT_ERROR = 'agent_error', 'Error de Agente'
        PERMISSION_BLOCKED = 'permission_blocked', 'Bloqueado por Permisos'

    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices,
        verbose_name='Tipo de evento'
    )
    agent = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Agente'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Timestamp'
    )
    value = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Valor',
        help_text='Ej: execution_time_ms'
    )
    metadata = models.JSONField(
        default=dict,
        verbose_name='Metadata',
        help_text='Información adicional específica del tipo de evento'
    )

    class Meta:
        verbose_name = 'Evento de Métrica'
        verbose_name_plural = 'Eventos de Métrica'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['agent', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.agent or 'N/A'} @ {self.timestamp}"
```

**Indexes Rationale**:

- `(event_type, timestamp)`: Para filtrar por tipo de evento y rango de fechas
- `(agent, timestamp)`: Para métricas por agente en rango de fechas

**Usage Pattern**:

- WorkflowRun: Registro completo para auditoría y detalle
- MetricEvent: Snapshot ligero para agregación rápida en `/api/metrics/`

## Testing Strategy

**Overview**: Este feature NO es apropiado para property-based testing porque consiste principalmente en:

- Operaciones de escritura a base de datos (side effects)
- Endpoints de API REST (CRUD operations)
- Agregación SQL (queries determinísticas)
- Integración con infraestructura (Django ORM, sessions)

No hay transformaciones de datos con propiedades universales que validen. Por lo tanto, usaremos **unit tests** para lógica de negocio, **integration tests** para endpoints de API, y **tests de integración con BD** para modelos y queries.

### Unit Tests

**Target**: `TraceabilityManager`, `MetricsAggregator`

**Test Cases**:

1. **test_create_run_sets_initial_state**
   - Crear WorkflowRun usando `TraceabilityManager.create_run()`
   - Verificar `final_state='created'`
   - Verificar `state_history` contiene entrada inicial

2. **test_update_run_agent_selection_transitions_to_running**
   - Crear run, luego llamar `update_run_agent_selection()`
   - Verificar `final_state='running'`
   - Verificar `state_history` contiene transición created → running

3. **test_complete_run_sets_final_state**
   - Crear run en state='running', llamar `complete_run()`
   - Verificar `final_state='completed'`
   - Verificar `execution_time_ms` se guardó correctamente

4. **test_fail_run_records_error_message**
   - Crear run, llamar `fail_run()` con error_message
   - Verificar `final_state='failed'`
   - Verificar `error_message` se guardó

5. **test_metrics_aggregator_counts_executions_by_agent**
   - Crear 3 runs con diferentes agents
   - Llamar `MetricsAggregator.get_summary_metrics()`
   - Verificar `executions_by_agent` contiene conteos correctos

6. **test_metrics_aggregator_filters_by_date_range**
   - Crear runs con diferentes timestamps
   - Llamar `get_summary_metrics(start_date, end_date)`
   - Verificar solo se incluyen runs dentro del rango

### Integration Tests (API Endpoints)

**Target**: `/api/actions/`, `/api/metrics/`, `/api/admin/actions/`

**Test Cases**:

1. **test_api_actions_returns_only_user_runs**
   - Crear 2 usuarios con runs cada uno
   - Autenticar como user1
   - GET `/api/actions/`
   - Verificar response solo contiene runs de user1

2. **test_api_actions_requires_authentication**
   - GET `/api/actions/` sin autenticación
   - Verificar HTTP 401 o redirect a login

3. **test_api_actions_paginates_results**
   - Crear 25 runs para un usuario
   - GET `/api/actions/` (default page_size=20)
   - Verificar response contiene 20 items
   - Verificar `next` link existe

4. **test_api_metrics_requires_privileged_profile**
   - Crear usuario con perfil='Usuario'
   - GET `/api/metrics/`
   - Verificar HTTP 403

5. **test_api_metrics_allows_administrador**
   - Crear usuario con perfil='Administrador'
   - GET `/api/metrics/`
   - Verificar HTTP 200

6. **test_api_metrics_returns_aggregated_data**
   - Crear varios runs con diferentes agents y states
   - GET `/api/metrics/`
   - Verificar estructura response contiene `total_executions`, `executions_by_agent`, etc.

7. **test_api_admin_actions_requires_administrador**
   - Crear usuario con perfil='Usuario IC'
   - GET `/api/admin/actions/`
   - Verificar HTTP 403

8. **test_api_admin_actions_returns_all_users_runs**
   - Crear 2 usuarios con runs
   - Autenticar como Administrador
   - GET `/api/admin/actions/`
   - Verificar response contiene runs de ambos usuarios

9. **test_api_admin_actions_filters_by_user_id**
   - GET `/api/admin/actions/?user_id=42`
   - Verificar response solo contiene runs de user_id=42

### Integration Tests (chat_view)

**Target**: Integración de trazabilidad en `/api/chat/`

**Test Cases**:

1. **test_chat_view_creates_workflow_run**
   - POST `/api/chat/` con query válido
   - Verificar WorkflowRun se creó con state='created'
   - Verificar user, conversation_id, user_message se guardaron

2. **test_chat_view_updates_run_on_success**
   - Mock n8n response exitosa
   - POST `/api/chat/`
   - Verificar WorkflowRun se actualizó con state='completed', agent_response

3. **test_chat_view_updates_run_on_failure**
   - Mock n8n error (timeout, connection error)
   - POST `/api/chat/`
   - Verificar WorkflowRun se actualizó con state='failed', error_message

4. **test_chat_view_records_execution_time**
   - POST `/api/chat/`
   - Verificar WorkflowRun.execution_time_ms > 0

5. **test_chat_view_includes_metadata_in_response**
   - Mock n8n response con metadata
   - POST `/api/chat/`
   - Verificar response JSON contiene `metadata.agent_used`, `metadata.execution_time_ms`

6. **test_traceability_does_not_block_user_response**
   - Mock fallo en `TraceabilityManager.update_run()` (simular error de BD)
   - POST `/api/chat/`
   - Verificar response al usuario es exitosa (trazabilidad no bloqueó)

### Model Tests

**Target**: `WorkflowRun`, `MetricEvent`

**Test Cases**:

1. **test_workflow_run_indexes_exist**
   - Inspeccionar modelo con `_meta.indexes`
   - Verificar índices en `(user, -created_at)`, `final_state`, etc.

2. **test_add_state_transition_updates_history**
   - Crear WorkflowRun
   - Llamar `add_state_transition('running')`
   - Verificar `state_history` contiene nueva entrada
   - Verificar `final_state='running'`

3. **test_metric_event_defaults**
   - Crear MetricEvent sin `value` ni `metadata`
   - Verificar `value=None`, `metadata={}`

### Template Tests

**Target**: `actions.html` template rendering

**Test Cases**:

1. **test_actions_page_requires_login**
   - GET `/actions/` sin autenticación
   - Verificar redirect a `/login/`

2. **test_actions_page_renders_user_runs**
   - Crear 3 runs para usuario
   - GET `/actions/`
   - Verificar template renderiza 3 action cards

3. **test_actions_page_color_codes_states**
   - Crear runs con states: completed, failed, running
   - GET `/actions/`
   - Verificar clases CSS correctas: `state-completed`, `state-failed`, `state-running`

4. **test_actions_page_paginates**
   - Crear 25 runs
   - GET `/actions/?page=1`
   - Verificar solo se muestran 20 runs
   - Verificar controles de paginación existen

### Test Coverage Goal

- **Unit tests**: >80% coverage en `TraceabilityManager`, `MetricsAggregator`
- **Integration tests**: 100% coverage de endpoints de API
- **Template tests**: Verificar rendering básico (no visual regression)

> **Interpretación del criterio ">80% coverage" (resuelta en checkpoint tarea 15):** El objetivo
> es **por componente**, no una línea de corte por archivo. Se cumple con: cobertura de las clases
> de servicio (`services.py`) ≥80% y cobertura **de comportamiento** de cada endpoint (test de éxito
>
> - test de rechazo/error). La cobertura global agregada (~91%) es referencia adicional, no el
>   criterio. `views.py` a nivel de línea puede quedar por debajo de 80% porque incluye ramas de error
>   de `chat_view` que pertenecen al spec cerrado `home-chat-orchestrator-contract`; eso no incumple
>   este objetivo.

### Test Execution

```bash
# Run all tests
cd app
python manage.py test core.tests.test_traceability

# Run with coverage
coverage run --source='core' manage.py test core.tests.test_traceability
coverage report
```

## Error Handling

### 1. Traceability Errors (Non-Blocking)

**Principle**: Los errores de trazabilidad NO deben bloquear la respuesta al usuario. La trazabilidad es crítica para auditoría, pero no crítica para la funcionalidad inmediata.

**Implementation**:

```python
# En TraceabilityManager
@staticmethod
def create_run(...) -> Optional[WorkflowRun]:
    try:
        with transaction.atomic():
            run = WorkflowRun.objects.create(...)
            return run
    except Exception as e:
        logger.error(
            "Failed to create WorkflowRun",
            extra={'error': str(e)},
            exc_info=True
        )
        return None  # No propagar excepción
```

**Error Scenarios**:

1. **BD no disponible durante create_run()**
   - Log error crítico
   - Retornar None
   - chat_view continúa y responde al usuario
   - Sistema queda sin registro de esta ejecución (gap en trazabilidad)

2. **JSON serialization error en system_decisions**
   - Convertir a string como fallback
   - Log warning
   - Continuar guardando el run

3. **Estado inválido en state transition**
   - Validar estado antes de agregar a state_history
   - Si inválido, log error y no actualizar estado
   - Mantener estado anterior

### 2. API Endpoint Errors (User-Facing)

**Implementation**:

```python
# En API views
@login_required
def api_actions(request):
    try:
        page = request.GET.get('page', 1)
        runs = WorkflowRun.objects.filter(user=request.user).order_by('-created_at')
        paginator = Paginator(runs, 20)
        page_obj = paginator.page(page)

        data = {
            'count': paginator.count,
            'next': ...,
            'previous': ...,
            'results': [...]
        }
        return JsonResponse(data, status=200)

    except PageNotAnInteger:
        return JsonResponse({'error': 'Número de página inválido'}, status=400)

    except EmptyPage:
        return JsonResponse({'error': 'Página fuera de rango'}, status=404)

    except Exception as e:
        logger.exception("Unexpected error in api_actions")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)
```

**Error Scenarios**:

1. **Usuario no autenticado**
   - HTTP 401 Unauthorized (Django @login_required maneja automáticamente)

2. **Perfil sin permisos para /api/metrics/**
   - HTTP 403 Forbidden
   - Body: `{"error": "No tiene permisos para acceder a las métricas"}`
   - **Nota**: La comparación de perfil debe usar `User.Profile.ADMINISTRADOR` y `User.Profile.USUARIO_IC` (constantes de TextChoices del modelo User), no strings literales

3. **Página de paginación inválida**
   - HTTP 400 Bad Request si page no es número
   - HTTP 404 Not Found si page > total pages

4. **Query date range inválido**
   - HTTP 400 Bad Request
   - Body: `{"error": "Formato de fecha inválido. Use ISO 8601."}`

### 3. n8n Integration Errors

**Scenarios**:

1. **n8n timeout**
   - WorkflowRun state: 'failed'
   - error_message: "n8n request timed out after 30s"
   - Response al usuario: HTTP 504 Gateway Timeout

2. **n8n connection refused**
   - WorkflowRun state: 'failed'
   - error_message: "Could not connect to n8n webhook"
   - Response al usuario: HTTP 503 Service Unavailable

3. **n8n invalid JSON response**
   - WorkflowRun state: 'failed'
   - error_message: "n8n returned invalid JSON"
   - Response al usuario: HTTP 502 Bad Gateway

**Implementation** (ya existe en chat_view):

```python
try:
    client = N8nClient()
    response_data = client.send(validated_payload)
except N8nTimeoutError as e:
    # Actualizar run como failed
    if run_id:
        TraceabilityManager.fail_run(run_id, str(e), ...)
    return JsonResponse({'error': '...'}, status=504)
# ... más casos
```

### 4. Database Errors

**Scenarios**:

1. **BD no disponible durante escritura**
   - Log crítico
   - Si es en trazabilidad: no bloquear respuesta al usuario
   - Si es en operación principal: HTTP 500

2. **Constraint violation (ej: conversationId demasiado largo)**
   - Truncar campo si es posible
   - Si no: log error y crear run con valor truncado

3. **Query timeout en métricas**
   - HTTP 504 Gateway Timeout
   - Body: `{"error": "La consulta tardó demasiado. Intente con rango de fechas más corto."}`

### 5. Edge Cases

**1. Usuario sin runs**

- `/api/actions/`: Retornar `{"count": 0, "results": []}`
- `/actions/`: Renderizar "No hay acciones registradas todavía."

**2. Filtro de date range sin resultados**

- `/api/metrics/?start_date=...&end_date=...`: Retornar métricas con valores en 0

**3. conversation_id duplicado**

- Permitido (múltiples requests en misma conversación)
- No es unique constraint

**4. user_message extremadamente largo (>10MB)**

- Validar en serializer (max 100.000 caracteres)
- HTTP 400 si excede

**5. system_decisions JSON inválido**

- Convertir a string como fallback: `system_decisions = json.dumps(invalid_json_str)`
- Log warning

**6. Paginación: page_size muy grande**

- Limitar a max 100 items por página
- Si user solicita más: usar 100

**7. MetricEvent creation en loop**

- Usar bulk_create() si se crean múltiples eventos
- Evitar N+1 queries

## Implementation Notes

### 1. Uso de Constantes de Perfil (User.Profile)

**CRÍTICO - Robustez de Comparaciones de Perfil**:

Todas las comparaciones de perfil en este spec deben usar las constantes de `TextChoices` definidas en el modelo `User` del spec `usuarios-demo-perfiles-permisos`:

```python
# CORRECTO: Usar constantes del modelo User
from core.models import User

if user.perfil == User.Profile.ADMINISTRADOR:
    # ...

if user.perfil in [User.Profile.ADMINISTRADOR, User.Profile.USUARIO_IC]:
    # ...
```

```python
# INCORRECTO: NO usar strings literales
if user.perfil == 'Administrador':  # ❌ Frágil, propenso a typos
    # ...

if user.perfil in ['Administrador', 'Usuario IC']:  # ❌ No refactor-safe
    # ...
```

**Constantes disponibles** (definidas en spec 2):

- `User.Profile.ADMINISTRADOR` → `'Administrador'`
- `User.Profile.USUARIO_IC` → `'Usuario IC'`
- `User.Profile.HEAVY_USER` → `'Heavy user'`
- `User.Profile.MACRO` → `'Macro'`
- `User.Profile.USUARIO` → `'Usuario'`

**Ubicaciones donde aplica**:

- `PermissionChecker.can_access_metrics()`: Verifica si perfil es Administrador o Usuario IC
- `PermissionChecker.can_access_admin_actions()`: Verifica si perfil es Administrador
- Views de API (`api_metrics`, `api_admin_actions`): Validación de permisos
- Tests: Comparaciones de perfil en assertions

**Beneficios**:

- Evita errores por typos (`'Administrador'` vs `'Administardor'`)
- Refactor-safe: Si el valor de perfil cambia, solo se actualiza en un lugar (el TextChoices)
- Autocompletado en IDEs
- Type checking si se usa mypy/pyright

**Dependencia**: Si el modelo `User` del spec `usuarios-demo-perfiles-permisos` no expone estas constantes como `User.Profile.ADMINISTRADOR`, deben agregarse explícitamente al modelo como `TextChoices` públicas.

### 2. Integración con chat_view

**Modificaciones requeridas en `core/views.py::chat_view()`**:

```python
@login_required
@require_http_methods(["POST"])
@csrf_protect
def chat_view(request):
    run_id = None
    start_time = time.time()

    try:
        # ... parseo y validación existente ...

        # 1. Crear WorkflowRun al inicio
        run = TraceabilityManager.create_run(
            user=request.user,
            conversation_id=conversation_id,
            user_message=query,
            agent_type=agent_type
        )
        run_id = run.id if run else None

        # 2. Llamar n8n (código existente)
        try:
            client = N8nClient()
            response_data = client.send(validated_payload)

            # 3. Actualizar run con éxito
            execution_time_ms = int((time.time() - start_time) * 1000)
            if run_id:
                TraceabilityManager.complete_run(
                    run_id=run_id,
                    agent_response=response_data.get('output', ''),
                    execution_time_ms=execution_time_ms,
                    metadata=response_data.get('metadata', {})
                )

            return JsonResponse(response_data, status=200)

        except N8nTimeoutError as e:
            # 4. Actualizar run con error
            execution_time_ms = int((time.time() - start_time) * 1000)
            if run_id:
                TraceabilityManager.fail_run(
                    run_id=run_id,
                    error_message=f"n8n timeout: {str(e)}",
                    execution_time_ms=execution_time_ms
                )
            return JsonResponse({'error': '...'}, status=504)

        # ... más casos de error ...

    except Exception as e:
        # 5. Catch-all: marcar como failed
        if run_id:
            execution_time_ms = int((time.time() - start_time) * 1000)
            TraceabilityManager.fail_run(run_id, str(e), execution_time_ms)
        logger.exception("Unexpected error in chat_view")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)
```

### 3. Transacción Separada Síncrona

**Objetivo**: Asegurar que la trazabilidad se persiste incluso si la operación principal falla, pero sin bloquear el request con async/Celery.

**Implementation**:

```python
# En TraceabilityManager
from django.db import transaction

@staticmethod
def create_run(...) -> Optional[WorkflowRun]:
    try:
        # Transacción separada: commit inmediato
        with transaction.atomic():
            run = WorkflowRun.objects.create(
                user=user,
                conversation_id=conversation_id,
                user_message=user_message,
                selected_agent=agent_type,
                final_state=WorkflowRun.ExecutionState.CREATED
            )
            run.add_state_transition(WorkflowRun.ExecutionState.CREATED)
            run.save()
            return run
    except Exception as e:
        logger.error("Failed to create WorkflowRun", exc_info=True)
        return None  # No propagar

@staticmethod
def update_run(...) -> None:
    try:
        with transaction.atomic():
            run = WorkflowRun.objects.select_for_update().get(id=run_id)
            # ... actualizar campos ...
            run.save()
    except WorkflowRun.DoesNotExist:
        logger.warning(f"WorkflowRun {run_id} not found for update")
    except Exception as e:
        logger.error("Failed to update WorkflowRun", exc_info=True)
```

**Razones para transacción síncrona simple**:

- MVP 1 no requiere alta concurrencia (100 usuarios demo, uso moderado)
- Evita complejidad de Celery/RQ en este stage
- Permite trazabilidad inmediata para debugging
- Transacción separada asegura commit incluso si request principal falla

**Migración futura a async** (MVP posterior):

- Si volumen crece o latencia es problema
- Cambiar `TraceabilityManager` para usar Celery tasks
- Mantener misma interfaz pública

### 3. Permissions Implementation

**PermissionChecker Class**:

```python
class PermissionChecker:
    @staticmethod
    def can_access_metrics(user: User) -> bool:
        """Solo Administrador y Usuario IC pueden ver métricas."""
        return user.perfil in ['Administrador', 'Usuario IC']

    @staticmethod
    def can_access_admin_actions(user: User) -> bool:
        """Solo Administrador puede ver acciones de otros usuarios."""
        return user.perfil == 'Administrador'

    @staticmethod
    def get_user_runs_queryset(user: User) -> QuerySet:
        """Retorna queryset de WorkflowRun filtrado por permisos del usuario."""
        return WorkflowRun.objects.filter(user=user)

    @staticmethod
    def get_all_runs_queryset(user: User, user_id: Optional[int] = None) -> QuerySet:
        """
        Retorna queryset de todas las WorkflowRun (solo Administrador).
        Si user_id se proporciona, filtra por ese usuario.
        """
        if not PermissionChecker.can_access_admin_actions(user):
            raise PermissionDenied("Solo los administradores pueden acceder a esta información")

        qs = WorkflowRun.objects.all()
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs
```

**Usage in Views**:

```python
@login_required
def api_metrics(request):
    if not PermissionChecker.can_access_metrics(request.user):
        return JsonResponse(
            {'error': 'No tiene permisos para acceder a las métricas'},
            status=403
        )
    # ... resto de lógica ...
```

### 4. MetricsAggregator Implementation Details

**Efficient SQL Queries**:

```python
from django.db.models import Count, Avg, Q

class MetricsAggregator:
    @staticmethod
    def get_summary_metrics(start_date=None, end_date=None) -> dict:
        # Base queryset
        qs = WorkflowRun.objects.all()

        # Filtrar por rango de fechas
        if start_date:
            qs = qs.filter(created_at__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__lte=end_date)

        # Total executions
        total = qs.count()

        # Executions by agent
        by_agent = dict(
            qs.values('selected_agent')
              .annotate(count=Count('id'))
              .values_list('selected_agent', 'count')
        )

        # Executions by state
        by_state = dict(
            qs.values('final_state')
              .annotate(count=Count('id'))
              .values_list('final_state', 'count')
        )

        # Avg execution time by agent
        avg_time = dict(
            qs.exclude(execution_time_ms__isnull=True)
              .values('selected_agent')
              .annotate(avg_ms=Avg('execution_time_ms'))
              .values_list('selected_agent', 'avg_ms')
        )

        # Error rate by agent
        error_rate = {}
        for agent in by_agent.keys():
            agent_total = qs.filter(selected_agent=agent).count()
            agent_failed = qs.filter(
                selected_agent=agent,
                final_state=WorkflowRun.ExecutionState.FAILED
            ).count()
            error_rate[agent] = agent_failed / agent_total if agent_total > 0 else 0.0

        return {
            'total_executions': total,
            'executions_by_agent': by_agent,
            'executions_by_state': by_state,
            'avg_execution_time_ms': avg_time,
            'error_rate': error_rate,
        }
```

**Performance Considerations**:

- Usa agregación SQL nativa (no Python loops)
- Filtra en BD, no en memoria
- Índices en `created_at`, `selected_agent`, `final_state` aceleran queries
- Con 10k registros: queries < 100ms

### 5. URL Configuration

**Agregar a `core/urls.py`**:

```python
from django.urls import path
from core import views

urlpatterns = [
    # ... rutas existentes ...
    path('api/actions/', views.api_actions, name='api_actions'),
    path('api/metrics/', views.api_metrics, name='api_metrics'),
    path('api/admin/actions/', views.api_admin_actions, name='api_admin_actions'),
    path('actions/', views.actions_page, name='actions_page'),
]
```

### 6. Static Files

**Crear archivos CSS/JS**:

1. **templates/css/actions.css**:
   - Estilos para action cards
   - Color coding por estado:
     - `.state-completed { border-left: 4px solid #22c55e; }`
     - `.state-failed { border-left: 4px solid #ef4444; }`
     - `.state-running { border-left: 4px solid #3b82f6; }`
     - `.state-pending_approval { border-left: 4px solid #eab308; }`
   - Layout responsive con grid/flexbox

2. **templates/js/actions.js**:
   - Función `showDetails(actionId)` para modal
   - Fetch details via AJAX (nuevo endpoint `/api/actions/<id>/`)
   - Renderizar detalles en modal

### 7. Database Migrations

**Migration sequence**:

1. **0001_add_workflow_run.py**: Crear modelo WorkflowRun
2. **0002_add_metric_event.py**: Crear modelo MetricEvent
3. **0003_add_indexes.py**: Agregar índices para performance

**Migration commands**:

```bash
cd app
python manage.py makemigrations core
python manage.py migrate
```

## Security Considerations

### 1. Data Exposure

**Problema**: Los campos de trazabilidad pueden contener datos sensibles (PII, información restringida del dataset).

**Solución**:

- **Permisos de lectura**: Solo el usuario que inició la acción puede ver su trazabilidad completa (`/api/actions/`)
- **Administrador**: Puede ver trazabilidad de todos (`/api/admin/actions/`)
- **No reintroduce contenido restringido**: Si el usuario con perfil Usuario consultó y el sistema bloqueó contenido restringido, el campo `agent_response` registra la respuesta bloqueada ("Encontré información relacionada... no tengo permiso..."), NO el contenido bloqueado original

### 2. SQL Injection

**Protección**: Django ORM automáticamente sanitiza queries. Nunca usar raw SQL con input de usuario sin parameterización.

### 3. XSS (Cross-Site Scripting)

**Protección**:

- Django templates auto-escape por defecto
- `agent_response` ya está sanitizado por `HTMLSanitizer` en chat_view antes de guardarse
- Template actions.html usa `{{ action.user_message|escape }}` automáticamente

### 4. CSRF

**Protección**: Todos los endpoints POST usan `@csrf_protect` (ya implementado en chat_view).

### 5. Authorization Bypass

**Protección**:

- Todos los endpoints usan `@login_required`
- Permisos verificados explícitamente con `PermissionChecker`
- Queryset filtrado por usuario antes de retornar datos

**Test crítico**: Verificar que usuario A no puede acceder a acciones de usuario B vía manipulación de parámetros.

## Performance Optimization

### 1. Database Indexes

**Critical indexes** (ya definidos en modelos):

- `WorkflowRun`: `(user, -created_at)` — para `/api/actions/` (filtra por user, ordena por fecha desc)
- `WorkflowRun`: `final_state` — para métricas por estado
- `WorkflowRun`: `selected_agent` — para métricas por agente
- `WorkflowRun`: `created_at` — para filtrado por fecha
- `MetricEvent`: `(event_type, timestamp)` — para métricas por tipo y fecha
- `MetricEvent`: `(agent, timestamp)` — para métricas por agente y fecha

**Impact**: Con índices, queries en 10k registros < 50ms. Sin índices: > 500ms.

### 2. Query Optimization

**N+1 Query Prevention**:

```python
# ❌ MAL: N+1 queries
runs = WorkflowRun.objects.filter(user=user)
for run in runs:
    print(run.user.email)  # Query adicional por cada run

# ✅ BIEN: 1 query con select_related
runs = WorkflowRun.objects.filter(user=user).select_related('user')
for run in runs:
    print(run.user.email)  # No query adicional
```

**Pagination**: Django REST Framework automáticamente limita resultados. Sin paginación, 10k registros serializados = respuesta de varios MB.

### 3. Caching (MVP posterior)

**Actual MVP 1**: Sin caching. Queries directas a BD.

**Futuro MVP 2+**:

- Cache de métricas agregadas (Redis)
- TTL: 5 minutos
- Invalidación: cuando se crea nuevo WorkflowRun

### 4. Data Volume Management

**MVP 1**: Retención indefinida (sin política de archivado).

**Estimación**:

- 100 usuarios demo
- 5 queries/usuario/día
- 30 días
- = 15.000 registros
- Tamaño promedio: 2 KB/registro
- Total: ~30 MB

**Conclusión**: Volumen manejable sin optimización compleja en MVP 1.

**MVP posterior**: Implementar archivado de registros > 90 días, compresión de campos JSON, particionamiento por fecha.

## Deployment Considerations

### 1. Environment Variables

**No new variables needed**. Sistema usa configuración existente:

- `DATABASE_URL`: Para SQLite/PostgreSQL
- `DJANGO_SECRET_KEY`: Para sesiones

### 2. Database Setup

```bash
# Run migrations
cd app
python manage.py migrate

# Verify models created
python manage.py shell
>>> from core.models import WorkflowRun, MetricEvent
>>> WorkflowRun.objects.count()
0
```

### 3. Initial Data

**No fixtures needed**. WorkflowRun se crea automáticamente cuando usuarios usan `/api/chat/`.

### 4. Monitoring

**Logs críticos**:

- Errores de trazabilidad: `logger.error("Failed to create WorkflowRun")`
- Errores de permisos: `logger.warning("User without permissions tried to access /api/metrics/")`
- Performance: `logger.info("Metrics query took X ms")`

**Log location**: `stdout` (capturado por Django logging config en `settings.py`)

## Dependencies

### Spec Dependencies

**This spec depends on**:

1. **usuarios-demo-perfiles-permisos**: User model con campo `perfil`, roles
2. **home-chat-orchestrator-contract**: Contrato de `/api/chat/`, estructura de metadata
3. **base-django-login-home**: Autenticación, sesiones, templates base

**Specs that depend on this**:

1. **rag-mails-dataset-permissions**: Debe registrar trazabilidad en cada consulta RAG
2. **trigger-comunicaciones-email**: Debe registrar trazabilidad en cada trigger de comunicación
3. **memoria-feedback-correcciones**: Usará WorkflowRun para historial conversacional

### Python Dependencies

**Already installed** (verificar en `app/requirements.txt`):

- Django >= 5.2
- djangorestframework
- dj-database-url

**New dependencies**: None

### Frontend Dependencies

**Already available**:

- Templates existentes: `login.html`, `home.html`
- CSS/JS structure: `templates/css/`, `templates/js/`

**New files to create**:

- `templates/actions.html`
- `templates/css/actions.css`
- `templates/js/actions.js`

## Migration Path

### From Current State to Spec Implementation

**Current state** (from code inspection):

- `/api/chat/` existe y funciona
- Integración con n8n implementada (N8nClient)
- User model con perfiles implementado
- NO existe trazabilidad

**Migration steps**:

1. **Crear modelos** (WorkflowRun, MetricEvent)
   - Run migrations
   - Verificar en Django admin

2. **Implementar TraceabilityManager**
   - Service class con métodos create_run, update_run, etc.
   - Tests unitarios

3. **Modificar chat_view**
   - Agregar llamadas a TraceabilityManager
   - Verificar que errores de trazabilidad no bloquean respuesta

4. **Implementar endpoints de API**
   - `/api/actions/`, `/api/metrics/`, `/api/admin/actions/`
   - Tests de integración

5. **Crear template actions.html**
   - HTML + CSS + JS
   - Verificar rendering

6. **Implementar MetricsAggregator**
   - Queries de agregación
   - Tests de performance

7. **Validación end-to-end**
   - Usuario hace query en `/api/chat/`
   - WorkflowRun se crea automáticamente
   - Usuario ve acción en `/actions/`
   - Administrador ve métricas en `/api/metrics/`

## Open Questions and Future Work

### Open Questions (for implementation phase)

1. **¿Incluir detalles de n8n response en system_decisions?**
   - Actual: Solo registramos agent_used, execution_time_ms
   - Opción: Registrar también records_found, intention_classification_confidence
   - **Resolución**: Registrar metadata completa recibida de n8n en system_decisions

2. **¿Color coding exacto para cada estado en actions.html?**
   - Definido: completed (verde), failed (rojo), running (azul), pending_approval (amarillo)
   - Pendiente: blocked_by_permissions, blocked_by_compliance, cancelled
   - **Resolución**: Todos los blocked\_\* y cancelled usan rojo (mismo tratamiento que failed)

3. **¿Formato de fecha en actions.html?**
   - Opción A: "17/04/2026 14:32"
   - Opción B: "Hace 2 horas"
   - **Resolución**: Usar formato A (absoluto) para consistencia con resto de Personal Stock

### Future Work (MVP 2+)

1. **Real-time updates**: WebSocket para actualizar `/actions/` en tiempo real cuando cambia estado
2. **Advanced filtering**: Filtrar por agent, estado, rango de fechas en UI
3. **Export**: Descargar trazabilidad como CSV/JSON
4. **Retention policy**: Archivar registros > 90 días
5. **Metrics dashboard**: Visualizaciones gráficas (charts) en lugar de JSON
6. **Async traceability**: Migrar a Celery para alto volumen
7. **Audit log**: Registro separado de acciones administrativas (ej: Administrador viendo acciones de otro usuario)

## Summary

Este diseño implementa trazabilidad obligatoria para Personal Stock MVP 1 mediante:

1. **Modelos Django**: WorkflowRun (trazabilidad completa) y MetricEvent (agregación)
2. **Integración transparente**: chat_view registra automáticamente cada ejecución
3. **Transacción separada síncrona**: Errores de trazabilidad no bloquean usuario
4. **APIs REST**: Endpoints para acciones del usuario, métricas agregadas, administración
5. **Página web**: Template Django con listado visual de acciones
6. **Permisos estrictos**: Solo usuario ve sus acciones; Administrador ve todas
7. **Performance**: Índices SQL, agregación eficiente, paginación

El diseño cumple con la regla crítica de `security-permissions.md`: **"Sin trazabilidad, una tarea de implementación no se considera completa, aunque el código funcione."**
