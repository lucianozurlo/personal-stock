# Devolución 129 — Validación acciones-trazabilidad-metricas, tarea 14.2

**Fecha:** 2026-07-01
**Spec:** acciones-trazabilidad-metricas
**Tarea:** 14.2 — Write template tests in core/tests.py

## Qué se implementó

Se agregó una clase de test al final de `app/core/tests.py` (después de
`MetricEventModelTest`, línea 2252), siguiendo el mismo estilo que las clases de
test ya existentes para este spec (`WorkflowRunModelTest`, `ApiActionsIntegrationTest`):

- `ActionsPageTemplateTest` (`app/core/tests.py:2257-2337`):
  - `test_actions_page_requires_login` (línea 2273)
  - `test_actions_page_renders_user_runs` (línea 2278)
  - `test_actions_page_color_codes_states` (línea 2294)
  - `test_actions_page_paginates` (línea 2320)

No se modificó `core/models.py`, `core/views.py`, `core/urls.py` ni
`templates/actions.html` — la vista `actions_page` y el template ya estaban
implementados y validados en tareas previas (9.1-9.5); esta tarea agrega
únicamente cobertura de test sobre ese comportamiento existente. No se
detectó ningún bug durante la implementación ni la verificación.

## Validación criterio por criterio (tasks.md, tarea 14.2)

| Criterio | Estado | Evidencia |
|---|---|---|
| test_actions_page_requires_login: GET /actions/ unauthenticated, verify redirect to /login/ | Sí | `app/core/tests.py:2273-2276`; `assertRedirects(response, '/login/?next=/actions/', fetch_redirect_response=False)`, consistente con `LOGIN_URL='/login/'` (`app/config/settings.py:157`) y `@login_required` en `actions_page` (`app/core/views.py:453`) |
| test_actions_page_renders_user_runs: create 3 runs, GET /actions/, verify 3 action cards rendered | Sí | `app/core/tests.py:2278-2292`; `assertContains(response, 'action-card', count=3)` contra `class="action-card state-{{ action.final_state }}"` (`templates/actions.html:33`) |
| test_actions_page_color_codes_states: create runs with different states, verify correct CSS classes | Sí | `app/core/tests.py:2294-2318`; runs con `final_state` en `COMPLETED`, `FAILED`, `RUNNING`; assert `'state-completed'`, `'state-failed'`, `'state-running'` presentes en el HTML renderizado |
| test_actions_page_paginates: create 25 runs, GET /actions/?page=1, verify only 20 runs shown and pagination controls present | Sí | `app/core/tests.py:2320-2337`; `assertContains(response, 'action-card', count=20)` (page_size=20 hardcodeado en `actions_page`, `app/core/views.py:456`), más `assertContains(response, 'class="pagination"')` y `assertContains(response, 'Siguiente')` |
| Requirement 6.2 (tabla/listado con acciones recientes del usuario) | Sí | Cubierto por `test_actions_page_renders_user_runs` |
| Requirement 6.3 (mostrar final_state por acción) | Sí | Cubierto por `test_actions_page_color_codes_states` vía `get_final_state_display` en el badge y la clase `state-*` |
| Requirement 6.4 (color coding por estado) | Sí | Cubierto por `test_actions_page_color_codes_states` |
| Requirement 6.6 (paginación con controles previous/next) | Sí | Cubierto por `test_actions_page_paginates` |
| Requirement 6.7 (solo usuarios autenticados, redirect a login) | Sí | Cubierto por `test_actions_page_requires_login` |

## Evidencia de comandos ejecutados

Tests nuevos en aislamiento (solicitado a la usuaria por restricción de entorno,
ver nota más abajo) y suite completa, corridos por la usuaria en su propia sesión
de shell:

```
manage.py test core (suite completa)
Ran 152 tests
OK
```

152 = 148 (gate de la tarea 14.1, devolución 128) + 4 (los tests nuevos de esta
tarea 14.2). Sin regresiones. Los 7 tests de `ChatViewTraceabilityIntegrationTest`
(tarea 13.1) y el fix de `selected_agent` en `TraceabilityManager.complete_run()`
que aparecen mencionados en la corrida ya estaban incluidos en el baseline de 148
— fueron implementados y validados en una sesión anterior (ver
`docs/devoluciones/126-...` y `docs/devoluciones/127-validacion-acciones-trazabilidad-metricas-tarea-13.1.md`,
veredicto `COMPLETED`), no son parte del trabajo de esta tarea 14.2.

Nota de entorno: no se ejecutaron los tests directamente desde esta sesión de
Claude Code porque correrlos requiere `DJANGO_SECRET_KEY`/`DATABASE_URL` reales
del `.env` del proyecto, y las reglas de `security-permissions.md` ("Nunca leer
ni mostrar el contenido de .env real") impiden a Claude Code hacer `source
../.env` directamente. Se le pidió a la usuaria correr el comando en su propia
sesión de shell (vía `!`), y ella confirmó el resultado arriba.

## Cambio adicional

Ninguno en esta tarea. (El único "cambio adicional" mencionado en la corrida —
el fix de `selected_agent` en `complete_run()` — pertenece a la tarea 13.1, ya
documentado y validado en la devolución 127; no se re-aplicó ni se re-valida
aquí para evitar duplicar una validación ya cerrada.)

## Alcance respetado

- No se tocaron `views.py`, `models.py`, `urls.py` ni `templates/actions.html`.
- No se renombró el producto.
- No se inventaron endpoints ni workflows fuera del spec.
- No se avanzó a la tarea 15 (checkpoint final).
- Único archivo modificado: `app/core/tests.py` (una clase de test nueva,
  `ActionsPageTemplateTest`, 4 métodos).

## Veredicto

Pendiente de validación por Kiro contra `requirements.md` y `tasks.md`. No se
marca la tarea como completed en este documento ni se realiza commit todavía,
conforme al protocolo de CLAUDE.md.
