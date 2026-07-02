from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Profile(models.TextChoices):
        ADMINISTRADOR = 'Administrador', 'Administrador'
        USUARIO_IC = 'Usuario IC', 'Usuario IC'
        HEAVY_USER = 'Heavy user', 'Heavy user'
        MACRO = 'Macro', 'Macro'
        USUARIO = 'Usuario', 'Usuario'

    email = models.EmailField(unique=True, verbose_name='Email')
    perfil = models.CharField(
        max_length=20,
        choices=Profile.choices,
        default=Profile.USUARIO,
        verbose_name='Perfil'
    )
    roles = models.ManyToManyField(
        'Role',
        blank=True,
        related_name='users',
        verbose_name='Roles'
    )
    cargo = models.CharField(max_length=100, blank=True, verbose_name='Cargo')
    es_focus = models.BooleanField(default=False, verbose_name='Es Focus')
    areas_focus = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Áreas Focus',
        help_text='Áreas separadas por coma'
    )
    es_aprobador_default = models.BooleanField(
        default=False,
        verbose_name='Es aprobador por defecto'
    )
    puede_aprobar = models.BooleanField(
        default=False,
        verbose_name='Puede aprobar comunicaciones'
    )
    avatar_url = models.URLField(
        blank=True,
        verbose_name='URL del avatar',
        help_text='URL externa o path relativo a static'
    )
    memoria_habilitada = models.BooleanField(
        default=True,
        verbose_name='Memoria conversacional habilitada'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['perfil']),
            models.Index(fields=['es_focus']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def has_restricted_access(self):
        return self.perfil == self.Profile.USUARIO

    def can_access_restricted_content(self):
        return self.perfil in [
            self.Profile.ADMINISTRADOR,
            self.Profile.USUARIO_IC,
            self.Profile.HEAVY_USER,
            self.Profile.MACRO,
        ]


class Role(models.Model):
    class RoleName(models.TextChoices):
        DISENADOR = 'Diseñador', 'Diseñador'
        DESARROLLADOR = 'Desarrollador', 'Desarrollador'
        REDACTOR = 'Redactor', 'Redactor'
        PRODUCTOR = 'Productor', 'Productor'
        GERENTE_CULTURA = 'Gerente Cultura', 'Gerente Cultura'
        GERENTE_IC = 'Gerente IC', 'Gerente IC'
        ESPECIALISTA = 'Especialista', 'Especialista'

    name = models.CharField(
        max_length=20,
        choices=RoleName.choices,
        unique=True,
        verbose_name='Nombre del rol'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción del rol'
    )

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['name']

    def __str__(self):
        return self.name


class WorkflowRun(models.Model):
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

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='workflow_runs',
        verbose_name='Usuario'
    )
    conversation_id = models.CharField(max_length=50, verbose_name='ID de conversación')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    execution_time_ms = models.IntegerField(null=True, blank=True, verbose_name='Tiempo de ejecución (ms)')
    user_message = models.TextField(verbose_name='Mensaje del usuario')
    detected_intention = models.CharField(max_length=100, blank=True, verbose_name='Intención detectada')
    selected_agent = models.CharField(max_length=100, verbose_name='Agente seleccionado')
    selection_reason = models.TextField(blank=True, verbose_name='Motivo de selección')
    permissions_applied = models.TextField(blank=True, verbose_name='Permisos aplicados')
    system_decisions = models.JSONField(default=dict, verbose_name='Decisiones del sistema')
    agent_response = models.TextField(blank=True, verbose_name='Respuesta del agente')
    error_message = models.TextField(null=True, blank=True, verbose_name='Mensaje de error')
    final_state = models.CharField(
        max_length=50,
        choices=ExecutionState.choices,
        default=ExecutionState.CREATED,
        verbose_name='Estado final'
    )
    state_history = models.JSONField(default=list, verbose_name='Historial de estados')

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
        self.state_history.append({
            'state': new_state,
            'timestamp': timezone.now().isoformat()
        })
        self.final_state = new_state


class MetricEvent(models.Model):
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
        verbose_name='Metadata'
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
