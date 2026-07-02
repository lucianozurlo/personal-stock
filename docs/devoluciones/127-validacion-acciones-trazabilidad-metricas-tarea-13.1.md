# Validación — Tarea 13.1: Write integration tests for /api/chat/ traceability

**Spec:** acciones-trazabilidad-metricas
**Fecha:** 2026-07-01
**Tarea:** 13.1 — "Write integration tests for /api/chat/ traceability in core/tests.py
(módulo único; ver docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md
— mismo criterio que 11.x)"
**Veredicto:** COMPLETED (validación Kiro OK)

---

## Qué se validó

Se agregaron 6 integration tests requeridos + 1 test de regresión del fix, en la clase
`ChatViewTraceabilityIntegrationTest` de `app/core/tests.py` (líneas ~2050-2189), que
ejercitan el endpoint `/api/chat/` (vista `chat_view` en `core/views.py`) mockeando
`core.views.N8nClient` para controlar respuestas de éxito y error de n8n sin depender de
una instancia real (coherente con el fallback de n8n de `tech.md` y con la regla de
`home-chat-orchestrator-contract` de respetar el shape del contrato).

Se revisó además el fix reportado en `TraceabilityManager.complete_run()`
(`app/core/services.py`) y su test dedicado.

**Método de verificación de Kiro:**

1. Lectura directa de los 7 tests en `app/core/tests.py` (líneas 2050-2189) contra el
   criterio de aceptación de la tarea 13.1 en `tasks.md`.
2. Lectura de `TraceabilityManager.complete_run()` en `app/core/services.py` para
   confirmar el fix `if metadata.get('agent_used'): run.selected_agent = metadata['agent_used']`.
3. Ejecución de la suite completa: `manage.py test core` → **145/145 OK** (708s).

---

## Resultados por criterio de tasks.md

| Criterio (tasks.md, tarea 13.1)                                                                          | Estado                               | Evidencia                                                                                                                                                                                                                                                                                        |
| -------------------------------------------------------------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `test_chat_view_creates_workflow_run`: POST valid query, verify WorkflowRun created with state='created' | Cumplido                             | `tests.py:2081-2096`. Assert `run.state_history[0]['state'] == ExecutionState.CREATED`, `user_message` y `conversation_id` correctos.                                                                                                                                                            |
| `test_chat_view_updates_run_on_success`: mock n8n success, verify state='completed' + agent_response     | Cumplido                             | `tests.py:2098-2110`. Assert `final_state == COMPLETED`, `'Respuesta de prueba' in agent_response`.                                                                                                                                                                                              |
| `test_chat_view_updates_run_on_failure`: mock n8n error, verify state='failed' + error_message           | Cumplido                             | `tests.py:2112-2125`. `N8nTimeoutError` → HTTP 504, `final_state == FAILED`, `'n8n timeout' in error_message`.                                                                                                                                                                                   |
| `test_chat_view_records_execution_time`: verify execution_time_ms > 0                                    | Cumplido                             | `tests.py:2127-2138`. Assert `execution_time_ms is not None` y `>= 0`. (Nota: el criterio del summary dice `> 0`; el test usa `>= 0`, correcto y más robusto porque un mock puede resolver en <1ms.)                                                                                             |
| `test_chat_view_includes_metadata_in_response`: mock metadata, verify response JSON contiene metadata    | Cumplido                             | `tests.py:2141-2154`. Assert `data['metadata']['agent_used'] == 'rag-mails'`, `records_found == 5`, `execution_time_ms` es int.                                                                                                                                                                  |
| `test_traceability_does_not_block_user_response`: fallo en trazabilidad, verify respuesta sigue OK       | Cumplido                             | `tests.py:2171-2189`. Mockea fallo de BD en `select_for_update` durante `complete_run`; assert HTTP 200 + `'output' in data`; el run queda en `CREATED` (la escritura de trazabilidad falló silenciosamente sin tirar la respuesta). Cubre Req 7.6 y Conflict 2 (transacción separada síncrona). |
| Requirements referenciados: 7.1-7.6, 9.1-9.6                                                             | Cumplido (con gap documentado abajo) | 7.1 (create run), 7.3 (update on success), 7.4 (update on error), 7.5/7.6 (partial-failure no bloquea), 9.1-9.6 (metadata en payload) cubiertos por los tests. 7.2 (update con agent selection antes de llamar al agente) — ver **Gap** abajo.                                                   |

**Evidencia de ejecución:**

- `manage.py test core` → **145/145 tests, OK** (708s). Sube de 138 (devolución 125) a
  145 = +7 (6 requeridos + 1 del fix). Sin regresiones. El traceback de `Exception:
Simulated DB failure during traceability update` que aparece en el log es la excepción
  intencional del test `test_traceability_does_not_block_user_response`, capturada y
  logueada por `complete_run` (no rompe el test).
- Variables de entorno: la suite se corrió con valores dummy de entorno para el test DB
  efímero (`DJANGO_SECRET_KEY`, `DATABASE_URL=sqlite`, `N8N_WEBHOOK_URL`), sin leer ni
  mostrar el `.env` real, conforme a `security-permissions.md`.

---

## Cambio adicional (fix validado)

Claude Code corrigió un bug real en `TraceabilityManager.complete_run()`
(`app/core/services.py`): antes no actualizaba `selected_agent` con el `agent_used` real
devuelto por n8n, dejando todo `WorkflowRun` con `selected_agent='auto'` en el caso normal.
Se agregó dentro del bloque `if metadata:`:

```python
if metadata.get('agent_used'):
    run.selected_agent = metadata['agent_used']
```

**Validado por Kiro:**

- El código está presente en `services.py` (método `complete_run`).
- El test `test_chat_view_updates_selected_agent_from_n8n_response` (`tests.py:2157-2169`)
  confirma que `run.selected_agent == 'rag-mails'` tras una respuesta de n8n con
  `metadata.agent_used='rag-mails'`.
- El fix es correcto y pertinente: sin él, Requirements 1.6, 4.3, 5.3, 6.3 y 10.6 quedaban
  rotos en la práctica (todo run mostraba `selected_agent='auto'`). El cambio está dentro
  del alcance de trazabilidad de este spec y no toca arquitectura ni contrato.

---

## Gap documentado — requiere decisión de spec (NO bloquea 13.1)

**Hallazgo:** Requirement 7 AC2 (y por extensión 2.3, 2.7) asume que Django clasifica la
intención y selecciona el agente "antes de llamar al agente", con transición de estado a
`running`. En la arquitectura real, decidida en el spec cerrado
`home-chat-orchestrator-contract`, esa clasificación la hace **n8n externamente**: el
contrato de respuesta solo expone `metadata: {agent_used, execution_time_ms,
records_found}`, sin `detected_intention` ni `selection_reason`.

**Efecto observado:**

- `TraceabilityManager.update_run_agent_selection()` (implementado en tarea 3.1) nunca se
  invoca desde `chat_view`, porque Django no tiene esos datos antes de llamar a n8n.
- `final_state` nunca transiciona por `running` (va de `created` directo a
  `completed`/`failed`).
- `detected_intention`, `selection_reason` y `permissions_applied` quedan vacíos.
- `selected_agent` sí se puebla, pero _a posteriori_ desde `metadata.agent_used` (fix
  arriba).

**Por qué no bloquea la tarea 13.1:** la 13.1 es una tarea de testing y sus 6 tests
requeridos reflejan correctamente el comportamiento real del sistema. El gap pertenece a
la integración (tarea 5.1, ya cerrada) y al diseño; es una decisión de spec, no un defecto
de los tests de 13.1. Los tests escritos son válidos y pasan.

**Recomendación de Kiro (pendiente de aprobación antes de editar el spec):** aplicar la
**Opción 2** con la justificación de la Opción 1 — documentar en `design.md` y
`requirements.md` que, dada la arquitectura de `home-chat-orchestrator-contract`, en MVP 1:

- el estado `running` y los campos `detected_intention` / `selection_reason` /
  `permissions_applied` quedan **preparados pero no poblados** (el modelo y el método
  `update_run_agent_selection` existen para MVP posterior);
- la clasificación de intención y selección de agente la hace n8n, no Django; esos campos
  solo se poblarán si un contrato futuro de n8n los expone;
- `selected_agent` sí se puebla desde `metadata.agent_used`.

Esto es coherente con `product.md` ("Si una parte no puede completarse en MVP 1, queda
marcada como preparada para MVP posterior — nunca se omite en silencio") y con `rules.md`
(no reabrir `home-chat-orchestrator-contract`). **Debe resolverse antes del checkpoint
final (tarea 15).** Por la regla de `rules.md` de esperar aprobación antes de tocar
`requirements.md`/`design.md` ante un conflicto, Kiro NO editó esos archivos en esta
validación: solo dejó el gap flageado aquí y en `PROGRESO.md`.

---

## Alcance respetado

- Claude Code tocó `app/core/tests.py` (clase nueva) y `app/core/services.py` (fix de
  `complete_run`).
- Kiro editó únicamente: `tasks.md` (marca 13/13.1 como `[x]`), `PROGRESO.md` (gate +
  historial + gap) y este documento de devolución.
- No se editó `requirements.md` ni `design.md` (el gap queda pendiente de decisión
  aprobada).
- No se reabrió `home-chat-orchestrator-contract`.
- No se leyó ni mostró el `.env` real.
- Tareas 14.1, 14.2 y 15 quedan pendientes.

## Veredicto final

**COMPLETED.** Los 6 criterios de aceptación de la tarea 13.1 están cumplidos y verificados
(145/145 tests OK), y el fix adicional de `selected_agent` está validado. El gap de Req 7
AC2 / 2.3 / 2.7 queda registrado como ítem de decisión de spec a resolver antes de la tarea
15; no bloquea el cierre de 13.1.
