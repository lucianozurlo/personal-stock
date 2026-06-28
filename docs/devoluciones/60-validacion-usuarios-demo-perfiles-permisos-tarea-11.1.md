# Validación tarea 11.1 — Registrar User y Role en Django Admin

**Spec:** usuarios-demo-perfiles-permisos
**Tarea:** 11.1
**Fecha:** 2026-06-23
**Archivo modificado:** `app/core/admin.py`

---

## Qué se implementó

Se registraron los modelos `User` y `Role` en el admin de Django:

- `UserAdmin` extendiendo `django.contrib.auth.admin.UserAdmin` (como `BaseUserAdmin`) — ver nota técnica abajo.
- `RoleAdmin` extendiendo `admin.ModelAdmin`.

**Nota técnica — base class:** La tarea dice "extendiendo de admin.ModelAdmin" pero el modelo `User` extiende `AbstractUser`. Usar `ModelAdmin` puro para un custom user model rompe el manejo de passwords (muestra el hash crudo) y el flujo de alta de usuarios. Se usó `django.contrib.auth.admin.UserAdmin` como base, que provee formularios de cambio de contraseña y fieldsets de permisos. Esta decisión está documentada en el plan de implementación.

---

## Criterios de aceptación (tasks.md 11.1)

| Criterio                                                       | Estado | Evidencia                                                                                                                                                                                                                            |
| -------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Configurar UserAdmin extendiendo base apropiada                | ✅ sí  | `class UserAdmin(BaseUserAdmin)` — `app/core/admin.py` línea 7                                                                                                                                                                       |
| Agregar campos custom al fieldset (perfil, roles, cargo, etc.) | ✅ sí  | `fieldsets` incluye secciones "Perfil Personal Stock" (perfil, roles, cargo, es_focus, areas_focus), "Permisos de aprobación" (es_aprobador_default, puede_aprobar), "Configuración" (avatar_url, memoria_habilitada) — líneas 17–33 |
| Configurar list_display con campos relevantes                  | ✅ sí  | `list_display = ('email', 'first_name', 'last_name', 'perfil', 'es_focus', 'is_active', 'is_staff')` — línea 8                                                                                                                       |
| Configurar list_filter por perfil y es_focus                   | ✅ sí  | `list_filter = ('perfil', 'es_focus', 'is_active', 'is_staff')` — línea 9                                                                                                                                                            |
| Configurar search_fields por email, first_name, last_name      | ✅ sí  | `search_fields = ('email', 'first_name', 'last_name')` — línea 10                                                                                                                                                                    |
| Registrar RoleAdmin con list_display y search                  | ✅ sí  | `@admin.register(Role)` con `list_display = ('name', 'description')` y `search_fields = ('name',)` — líneas 37–40                                                                                                                    |

---

## Verificación técnica

```
$ set -a && source ../.env && set +a && python3 manage.py check
System check identified no issues (0 silenced).
```

---

## Veredicto preliminar

Todos los criterios de aceptación de la tarea 11.1 están cumplidos. El sistema Django reporta 0 issues. Listo para validación Kiro.

---

## Validación Kiro

**Fecha:** 2026-06-23
**Validado contra:** requirements.md (Requirement 8 AC1 — campos de usuario)

### Análisis

1. **Base class UserAdmin:** Extiende `BaseUserAdmin` (django.contrib.auth.admin.UserAdmin). Decisión correcta: `ModelAdmin` puro no maneja passwords correctamente en custom user models. Requirement 8 no especifica base class, por lo que esta decisión técnica es válida.

2. **Campos expuestos:** Todos los campos del Requirement 8 AC1 están presentes en fieldsets:
   - perfil, roles, cargo, es_focus, areas_focus
   - es_aprobador_default, puede_aprobar
   - avatar_url, memoria_habilitada
     ✅ Completo

3. **Gestión operativa:** list_display, list_filter, search_fields configurados con campos relevantes para buscar y filtrar usuarios por perfil, es_focus, email, nombre. ✅

4. **RoleAdmin:** Registrado con display y search correctos. ✅

5. **Verificación técnica:** `python3 manage.py check` → 0 issues. ✅

### Veredicto

**✅ APPROVED — La tarea 11.1 cumple su criterio de aceptación y es consistente con requirements.md.**

**Acción:** Marcar tarea 11.1 como [x] en tasks.md y actualizar PROGRESO.md con next: tarea 12.1.
