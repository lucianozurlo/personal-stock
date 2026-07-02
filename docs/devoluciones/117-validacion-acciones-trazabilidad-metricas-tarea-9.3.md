# Reporte Tarea 9.3 - actions.js (showDetails + endpoint de detalle)

**Fecha:** 30 de junio de 2026
**Spec:** acciones-trazabilidad-metricas
**Tarea:** 9.3 — Create actions.js in templates/js/actions.js
**Reportado por:** Claude Code
**Estado:** ⏳ PENDIENTE DE VALIDACIÓN POR KIRO (este documento es el reporte de Claude Code, no un veredicto de Kiro)

---

## Qué se implementó

1. `templates/js/actions.js` (nuevo archivo): funciones `window.showDetails(actionId)` y `window.closeModal()` consumidas por `templates/actions.html` (ya existente desde la tarea 9.1), más cierre del modal con tecla `Escape`.
2. `app/core/views.py`: nueva vista `api_action_detail(request, action_id)` que devuelve el detalle completo de un `WorkflowRun`, restringido al usuario dueño del registro (`get_object_or_404(WorkflowRun, id=action_id, user=request.user)` → 404 si no es del usuario autenticado).
3. `app/core/urls.py`: nueva ruta `api/actions/<int:action_id>/` → `views.api_action_detail`, agregada inmediatamente después de `api/actions/`.

Se implementó el endpoint real (no un placeholder), ya que el modelo `WorkflowRun` ya tenía todos los campos necesarios y un placeholder hubiese dejado el Requirement 6.5 sin cumplir de verdad.

---

## Criterios de aceptación (tasks.md tarea 9.3 + Requirement 6.5) — evaluación punto por punto

### Criterio 1: Implementar `showDetails(actionId)` que hace fetch AJAX y muestra el resultado en el modal

**Cumplido:** Sí
**Evidencia:** `templates/js/actions.js`, función `window.showDetails` (líneas ~93–112): abre el modal (`openModal()`), muestra estado de carga, hace `fetch('/api/actions/' + actionId + '/', {credentials: 'same-origin'})`, y en éxito llama a `renderDetail(data)`; en error llama a `renderError(...)`.

### Criterio 2: Crear endpoint `/api/actions/<id>/` que devuelva el detalle completo de la acción

**Cumplido:** Sí (implementación real, no placeholder)
**Evidencia:**
- `app/core/urls.py`: `path('api/actions/<int:action_id>/', views.api_action_detail, name='api_action_detail')`.
- `app/core/views.py`, función `api_action_detail` (decoradores `@login_required`, `@require_http_methods(["GET"])`, mismo patrón que `api_actions`/`api_metrics`/`api_admin_actions`).
- Ownership: `get_object_or_404(WorkflowRun, id=action_id, user=request.user)` se ejecuta **fuera** del bloque `try/except Exception` para que `Http404` no sea capturado y convertido en un 500 (`Http404` es subclase de `Exception`); así el 404 real llega al cliente.

### Criterio 3 (Requirement 6.5): El detalle incluye `user_message` completo (no truncado)

**Cumplido:** Sí
**Evidencia:** `api_action_detail` devuelve `'user_message': run.user_message` sin truncar (a diferencia de `api_actions`, que sí trunca a 100 caracteres). `actions.js` lo renderiza en el bloque "Mensaje completo".

### Criterio 4 (Requirement 6.5): El detalle incluye `agent_response`

**Cumplido:** Sí
**Evidencia:** Campo `'agent_response': run.agent_response` en la respuesta JSON; renderizado en bloque "Respuesta del agente" en `actions.js`.

### Criterio 5 (Requirement 6.5): El detalle incluye `system_decisions`

**Cumplido:** Sí
**Evidencia:** Campo `'system_decisions': run.system_decisions` (JSON); `actions.js` lo formatea con `JSON.stringify(value, null, 2)` dentro de un `<pre>` en el bloque "Decisiones del sistema".

### Criterio 6 (Requirement 6.5): El detalle incluye `permissions_applied`

**Cumplido:** Sí
**Evidencia:** Campo `'permissions_applied': run.permissions_applied`; renderizado en bloque "Permisos aplicados".

### Criterio 7 (Requirement 6.5): El detalle incluye `error_message` si existe

**Cumplido:** Sí
**Evidencia:** Campo `'error_message': run.error_message`; en `actions.js`, `renderDetail()` solo agrega el bloque "Error" si `data.error_message` es truthy (condicional `errorBlock`).

### Criterio 8: No reintroducir vulnerabilidades XSS al mostrar datos potencialmente generados por usuario en el modal

**Cumplido:** Sí
**Evidencia:** Todo el contenido textual interpolado en el HTML del modal pasa por `escapeHtml()` (usa `div.textContent` → `div.innerHTML`) antes de insertarse, incluyendo `user_message`, `agent_response`, `permissions_applied`, `error_message` y el JSON de `system_decisions`. Ningún campo se inyecta crudo en `innerHTML`.

---

## Verificación técnica realizada

- `python3 -c "ast.parse(...)"` sobre `core/views.py` y `core/urls.py`: **sintaxis OK**.
- `node --check templates/js/actions.js`: **sintaxis OK**.

## Limitación de esta sesión (no se simula que se ejecutó algo que no corrió)

**No pude correr `python -Wa manage.py test` ni `python manage.py check`** en este entorno sandbox: `config/settings.py` requiere `DJANGO_SECRET_KEY` desde el entorno, y el repo tiene una regla de denegación explícita que bloquea leer o `source`-ear el `.env` real (correctamente, por `security-permissions.md`). No intenté eludir esa restricción.

**Pendiente de confirmar por el usuario en su propio shell** (donde el entorno ya está configurado):

```bash
cd app
python -Wa manage.py test
```

Si algún test existente se rompe por este cambio, avisar para corregirlo antes de pedir validación a Kiro.

---

## Archivos modificados

| Archivo                      | Acción          | Detalle                                                              |
| ----------------------------- | --------------- | --------------------------------------------------------------------- |
| `templates/js/actions.js`     | Creado (nuevo)  | `showDetails`, `closeModal`, helpers de escape/formateo JSON         |
| `app/core/views.py`           | Modificado      | Import `get_object_or_404`, import `WorkflowRun`, nueva vista `api_action_detail` |
| `app/core/urls.py`            | Modificado      | Nueva ruta `api/actions/<int:action_id>/`                            |

No se tocó `templates/actions.html` ni `templates/css/actions.css` (cerrados en 9.1/9.2), ni ningún archivo fuera del alcance de la tarea 9.3.

---

## Cambio adicional

Ninguno más allá de lo descrito (no se detectaron bugs en el código preexistente durante esta tarea).

---

## Próximos pasos (los hace el humano)

1. Confirmar `python -Wa manage.py test` en su entorno (con `DJANGO_SECRET_KEY` ya configurado) y reportar resultado.
2. Llevar este reporte a Kiro junto con el prompt generado para validación contra `requirements.md` y `tasks.md`.
3. Si Kiro valida: marcar `9.3` como `[x]` en `tasks.md`, actualizar `PROGRESO.md`, y recién ahí pedir el commit.
4. Si Kiro no valida: volver al punto 1 del protocolo dentro de la misma tarea 9.3.
