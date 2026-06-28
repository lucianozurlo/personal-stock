from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Role, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'perfil', 'es_focus', 'is_active', 'is_staff')
    list_filter = ('perfil', 'es_focus', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('last_name', 'first_name')
    filter_horizontal = ('roles', 'groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Datos personales', {'fields': ('first_name', 'last_name')}),
        ('Perfil Personal Stock', {'fields': ('perfil', 'roles', 'cargo', 'es_focus', 'areas_focus')}),
        ('Permisos de aprobación', {'fields': ('es_aprobador_default', 'puede_aprobar')}),
        ('Configuración', {'fields': ('avatar_url', 'memoria_habilitada')}),
        ('Permisos Django', {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas', {'classes': ('collapse',), 'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'perfil'),
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
