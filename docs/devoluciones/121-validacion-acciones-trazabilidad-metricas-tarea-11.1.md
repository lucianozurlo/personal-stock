# Validación — Tarea 11.1: Write unit tests for TraceabilityManager

**Spec:** acciones-trazabilidad-metricas
**Fecha:** 2026-07-01
**Tarea:** 11.1 — "Write unit tests for TraceabilityManager in core/tests.py (módulo
único; ver docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md)"

---

## Qué se validó

Se agregaron 4 unit tests para `TraceabilityManager` (`app/core/services.py` líneas
12–97), cubriendo sus 4 métodos públicos: `create_run`, `update_run_agent_selection`,
`complete_run` y `fail_run`. Los tests se agregaron como clase nueva
`TraceabilityManagerTest` al final de `app/core/tests.py` (líneas 1580–1673), **no** en
un paquete `core/tests/` — ver sección "Cambio adicional" más abajo.

**Método:** `TestCase` estándar de Django (transacción por test, rollback automático),
sin mocks — se ejercita `TraceabilityManager` contra un `WorkflowRun` real creado en cada
test, con un `User` de prueba (`trace_test@example.com`, perfil Administrador) creado en
`setUp`.

---

## Resultados por criterio de tasks.md

| Criterio (tasks.md, tarea 11.1) | Estado | Evidencia |
|---|---|---|
| `test_create_run_sets_initial_state`: verify `final_state='created'` and `state_history` has initial entry | Cumplido | `app/core/tests.py:1600-1610`. Asserts: `run.final_state == WorkflowRun.ExecutionState.CREATED`, `len(run.state_history) == 1`, `state_history[0]['state'] == CREATED`. Test pasa: ver output de corrida abajo. |
| `test_update_run_agent_selection_transitions_to_running`: verify state transition created → running | Cumplido | `app/core/tests.py:1613-1636`. Asserts: `run.final_state == RUNNING`, `selected_agent == 'rag-mails'`, `detected_intention == 'consulta_historial_mails'`, secuencia de `state_history` == `[created, running]`. Test pasa. |
| `test_complete_run_sets_final_state`: verify `final_state='completed'` and `execution_time_ms` saved | Cumplido | `app/core/tests.py:1638-1655`. Asserts: `run.final_state == COMPLETED`, `execution_time_ms == 450`, `agent_response == '<p>Respuesta</p>'`. Test pasa. |
| `test_fail_run_records_error_message`: verify `final_state='failed'` and `error_message` saved | Cumplido | `app/core/tests.py:1657-1673`. Asserts: `run.final_state == FAILED`, `error_message == 'n8n timeout: Request timed out'`, `execution_time_ms == 30000`. Test pasa. |
| Requirements referenciados: 1.1, 2.2, 2.3, 2.4, 2.5 | Cumplido | 1.1 (WorkflowRun creado con `state="created"` antes de llamar al agente) cubierto por `test_create_run_sets_initial_state`; 2.2 (estado inicial `created`) idem; 2.3 (transición a `running`) cubierto por `test_update_run_agent_selection_transitions_to_running`; 2.4 (transición a `completed`) cubierto por `test_complete_run_sets_final_state`; 2.5 (transición a `failed`) cubierto por `test_fail_run_records_error_message`. |

**Evidencia de ejecución** (corrida por el usuario, ya que requiere `DJANGO_SECRET_KEY`
del `.env` real, que Claude Code tiene prohibido leer por `security-permissions.md`):

- `python3 -Wa manage.py test core.tests.TraceabilityManagerTest -v 2` → **4/4 tests, OK**
- `python3 -Wa manage.py test core.tests -v 2` (suite completa) → **127/127 tests, OK**
  — sube desde 123 (checkpoint tarea 10, devolución 120) a 127, es decir +4, exactamente
  los tests nuevos de esta tarea. Ningún test preexistente se rompió ni se perdió.

---

## Cambio adicional

**Corrección de `tasks.md` (tarea 11.1):** el texto original de la tarea pedía crear
`core/tests/test_traceability.py` (un paquete `tests/`). Al leer la estructura real del
proyecto, `app/core/tests.py` ya existe como **módulo único** con ~123 tests de los specs
`base-django-login-home`, `usuarios-demo-perfiles-permisos` y
`home-chat-orchestrator-contract`. Python no permite que coexistan `core/tests.py` y
`core/tests/` en la misma carpeta (conflicto de import), y este mismo conflicto ya se
resolvió antes en este proyecto: `docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md`
documenta la decisión de mantener el módulo único por esta razón. Desde entonces, ~15
devoluciones posteriores (specs `usuarios-demo-perfiles-permisos` y
`home-chat-orchestrator-contract`) referencian tests puntuales con rutas
`core.tests.NombreDeClase` (ej. `core.tests.ChatViewIntegrationTest`,
`core.tests.DatasetFilterPerformanceTest`).

Se consultó al usuario (no a Kiro, por tratarse de una decisión de estructura de
archivos ya precedente en el propio historial del proyecto) y se confirmó mantener
`core/tests.py` único. Se corrigió la línea de la tarea 11.1 en
`.kiro/specs/acciones-trazabilidad-metricas/tasks.md` para que diga explícitamente
"in core/tests.py (módulo único...)" en vez de "in core/tests/test_traceability.py",
citando la devolución 70 como justificación, para que quede consistente con la decisión
ya documentada y no vuelva a generar ambigüedad en tareas futuras (11.2, 12.x, 13.1, 14.x
también mencionan rutas `core/tests/...` en tasks.md original y deberán resolverse igual
cuando les toque turno).

## Alcance respetado

- Solo se tocó `app/core/tests.py` (agregado al final, sin modificar tests existentes) y
  `.kiro/specs/acciones-trazabilidad-metricas/tasks.md` (corrección de una línea dentro
  de la tarea 11.1).
- No se tocó `core/services.py`, `core/models.py` ni ningún otro archivo de código fuente.
- No se implementó la tarea 11.2 (`MetricsAggregator`) ni ninguna otra tarea.
- No se rediseñaron templates, no se renombró el producto, no se inventaron endpoints.
- No se leyó ni se mostró contenido de `.env` real en ningún momento; al necesitarse para
  correr los tests, se le pidió al usuario que ejecutara los comandos en su propia shell.

## Veredicto

Pendiente de validación por Kiro contra `requirements.md` y `tasks.md`. No se marca la
tarea 11.1 como completed en este documento ni se realiza commit todavía, conforme al
protocolo de CLAUDE.md.
