# Devolución 130 — Validación Kiro: acciones-trazabilidad-metricas, tarea 14.2

**Fecha:** 2026-07-01
**Spec:** acciones-trazabilidad-metricas
**Tarea:** 14.2 — Write template tests in core/tests.py
**Veredicto:** ✅ COMPLETED

---

## Alcance de la tarea

La tarea 14.2 pide escribir tests de template para `GET /actions/` en `core/tests.py`,
cubriendo los siguientes criterios de aceptación del Requirement 6:

- **6.2** — La página muestra una lista/cards con las acciones recientes del usuario.
- **6.3** — Cada acción muestra sus campos (mensaje truncado, agente, estado, timestamp, tiempo).
- **6.4** — Color coding por estado.
- **6.6** — Paginación con controles previous/next.
- **6.7** — Solo accesible a usuarios autenticados (redirect a login si no).

No aplica property-based testing (ver Notes de tasks.md: este spec usa unit e integration tests).

---

## Validación contra requirements.md y tasks.md

Kiro revalidó de forma independiente, no solo por el reporte de Claude Code:
leyó `templates/actions.html`, la clase `ActionsPageTemplateTest` en `app/core/tests.py`
(líneas 2257-2337) y corrió la suite.

| Criterio (tasks.md 14.2)                                                      | Requirement | Estado      | Evidencia verificada por Kiro                                                                                                                                                                                                                       |
| ----------------------------------------------------------------------------- | ----------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| test_actions_page_requires_login: GET /actions/ sin auth → redirect a /login/ | 6.7         | ✅ Cumplido | `tests.py:2272-2275`, `assertRedirects(..., '/login/?next=/actions/')`. Test corrido: OK.                                                                                                                                                           |
| test_actions_page_renders_user_runs: 3 runs → 3 action cards                  | 6.2, 6.3    | ✅ Cumplido | `tests.py:2277-2291`, `assertContains(response, 'action-card', count=3)`. Template renderiza `<div class="action-card ...">` con timestamp, badge de estado, mensaje truncado (`truncatewords:20`), agente y `execution_time_ms`. Test corrido: OK. |
| test_actions_page_color_codes_states: clases CSS por estado                   | 6.3, 6.4    | ✅ Cumplido | `tests.py:2293-2317`, verifica `state-completed`, `state-failed`, `state-running`. Template aplica `class="action-card state-{{ action.final_state }}"`. Test corrido: OK.                                                                          |
| test_actions_page_paginates: 25 runs → 20 mostrados + controles               | 6.6         | ✅ Cumplido | `tests.py:2319-2336`, `assertContains(..., 'action-card', count=20)` + `class="pagination"` + `Siguiente`. Template usa `page_obj` con bloque `{% if page_obj.paginator.num_pages > 1 %}` y links Anterior/Siguiente. Test corrido: OK.             |

**Requirements 6.2, 6.3, 6.4, 6.6, 6.7:** todos cubiertos por los 4 tests.

Nota: Req 6.5 (click en acción abre modal con detalle completo) no está en el alcance
de la tarea 14.2 (no figura en su lista de subtareas ni en su `_Requirements:`). El
template incluye el modal `#detailsModal` y el botón `showDetails()`, correspondiente a
las tareas 9.1/9.3, ya validadas (devoluciones 115, 117). No se re-valida aquí.

---

## Verificación de ejecución (independiente)

Kiro corrió los tests con variables de entorno de prueba (no se leyó el `.env` real,
por `security-permissions.md`):

- `manage.py test core.tests.ActionsPageTemplateTest` → **4/4 OK**.
- `manage.py test core` (suite completa) → **152/152 OK**, sin regresiones.

Esto confirma el reporte de Claude Code (148 previos del gate de 14.1 + 4 nuevos = 152).

Los 7 tests de `ChatViewTraceabilityIntegrationTest` y el fix de `selected_agent`
mencionados en la corrida pertenecen a la tarea 13.1 (validada en devolución 127,
veredicto COMPLETED) y no forman parte de esta tarea — coincide con lo que reportó
Claude Code.

---

## Efecto en tasks.md

- `14.2` marcada `[x]`.
- `14` (parent) auto-completa: sus dos hijas (14.1, 14.2) quedan completed → marcada `[x]`.

Líneas modificadas:

```
- [x] 14. Write model and template tests
  ...
  - [x] 14.2 Write template tests in core/tests.py (módulo único; ...)
```

---

## Gap pendiente antes del checkpoint final (tarea 15)

Sigue abierto el gap documentado en la devolución 127, que **no bloquea 14.2** pero
**debe resolverse antes/durante la tarea 15**:

- **Req 7 AC2 / 2.3 / 2.7** asumen que Django clasifica la intención y transiciona el
  estado a `running` antes de llamar al agente. En la arquitectura real
  (`home-chat-orchestrator-contract`), esa clasificación la hace **n8n**; el contrato
  solo expone `metadata {agent_used, execution_time_ms, records_found}`.
- Efecto: `update_run_agent_selection()` no se invoca desde `chat_view`, el `final_state`
  nunca pasa por `running`, y `detected_intention` / `selection_reason` /
  `permissions_applied` quedan vacíos.
- Recomendación de Kiro: **Opción 2** — marcar esos campos y el estado `running` como
  "preparados pero no poblados en MVP 1" en `design.md` / `requirements.md`, con la razón
  de la Opción 1 (la clasificación la hace n8n). Pendiente de aprobación del usuario
  antes de editar el spec.

---

## Próximo paso

Paso 3.4 — implementar **tarea 15** (checkpoint final end-to-end) con Claude Code en
sesión nueva, incluyendo la resolución del gap Req 7 AC2 / 2.3 / 2.7.
