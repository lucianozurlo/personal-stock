from django.contrib.auth.models import AbstractUser
from django.db import models


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
