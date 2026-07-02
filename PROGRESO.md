# Estado del proyecto Personal Stock MVP 1

Última actualización: 2026-07-01 (acciones-trazabilidad-metricas completed)

---

## Spec actual en ejecución

**Spec:** rag-mails-dataset-permissions
**Tarea actual:** —
**Estado:** Sin empezar (pendiente Paso 3.1 — requirements)

---

## Último gate pasado

**Gate:** acciones-trazabilidad-metricas completed — spec cerrado, validación Kiro OK
**Fecha:** 2026-07-01

**Evidencia:**

- Tarea 15 (Final checkpoint - End-to-end validation) validada exitosamente:
  - Flujo end-to-end verificado: user query → WorkflowRun created → n8n llamado → WorkflowRun updated → metadata en response → acción visible en /actions/ → métricas en /api/metrics/ (admin). 6/6 criterios de flujo cumplidos con test citado por cada uno.
  - Suite completa: 152 tests, 0 failures, 0 errors.
  - **Criterio ">80% coverage" resuelto (interpretación por componente, no por archivo):** services.py 83% (≥80% clases de servicio ✓), endpoints con cobertura de comportamiento 100% (éxito + rechazo/error ✓), global 91%. views.py 72% a nivel de línea NO incumple: incluye ramas de error de chat_view que pertenecen a home-chat-orchestrator-contract (spec cerrado). Decisión documentada en design.md (Test Coverage Goal).
  - **Gap Req 7 AC2 / 2.3 / 2.7 resuelto (Opción 2, aprobado por usuario):** documentado en requirements.md (Req 7 AC2 reescrito al comportamiento real + notas de limitación en 2.3; nueva Decision 7) y design.md (State Transition Rules + nota). En MVP 1, el estado 'running' y los campos detected_intention/selection_reason/permissions_applied quedan PREPARADOS pero NO POBLADOS: la clasificación de intención y selección de agente las hace n8n, no Django. update_run_agent_selection() existe y está unit-testeado pero no se invoca desde chat_view. selected_agent sí se puebla desde metadata.agent_used. NO se reabrió home-chat-orchestrator-contract; NO se creó subtarea 15.1; NO se movió al spec 9.
  - Spec maestro actualizado: acciones-trazabilidad-metricas → completed.
- **Spec acciones-trazabilidad-metricas cerrado**: todas las tareas (1.1–14.2 + 15) completed y validadas.

---

## Next

**Paso 3.1:** Requirements de rag-mails-dataset-permissions con Kiro (sesión nueva)

- Dependencias satisfechas: usuarios-demo-perfiles-permisos (completed), home-chat-orchestrator-contract (completed), acciones-trazabilidad-metricas (completed).
- Nota de paralelismo (spec maestro): rag-mails-dataset-permissions y trigger-comunicaciones-email pueden desarrollarse en paralelo entre sí; ambas ya tienen sus dependencias directas en completed.
- Decisión 3 del spec maestro: el dataset se indexa (JSONL compacto o SQLite FTS5), no se carga completo en memoria por consulta.

---

## Historial de validaciones Kiro

| Fecha      | Spec                            | Tarea | Veredicto | Documento                                                                          |
| ---------- | ------------------------------- | ----- | --------- | ---------------------------------------------------------------------------------- |
| 2025-01-28 | base-django-login-home          | 1.1   | completed | docs/devoluciones/01-validacion-base-django-login-home-tarea-1.1.md                |
| 2025-01-28 | base-django-login-home          | 1.2   | completed | docs/devoluciones/02-validacion-base-django-login-home-tarea-1.2.md                |
| 2025-01-28 | base-django-login-home          | 2.1   | completed | docs/devoluciones/03-validacion-base-django-login-home-tarea-2.1.md                |
| 2025-01-28 | base-django-login-home          | 2.2   | completed | docs/devoluciones/04-validacion-base-django-login-home-tarea-2.2.md                |
| 2025-01-28 | base-django-login-home          | 3.1   | completed | docs/devoluciones/05-validacion-base-django-login-home-tarea-3.1.md                |
| 2025-01-28 | base-django-login-home          | 3.2   | completed | docs/devoluciones/06-validacion-base-django-login-home-tarea-3.2.md                |
| 2025-01-28 | base-django-login-home          | 3.3   | completed | docs/devoluciones/07-validacion-base-django-login-home-tarea-3.3.md                |
| 2025-01-28 | base-django-login-home          | 3.4   | completed | docs/devoluciones/08-validacion-base-django-login-home-tarea-3.4.md                |
| 2025-01-28 | base-django-login-home          | 3.5   | completed | docs/devoluciones/09-validacion-base-django-login-home-tarea-3.5.md                |
| 2025-01-28 | base-django-login-home          | 3.6   | completed | docs/devoluciones/10-validacion-base-django-login-home-tarea-3.6.md                |
| 2025-01-28 | base-django-login-home          | 4.1   | completed | docs/devoluciones/11-validacion-base-django-login-home-tarea-4.1.md                |
| 2025-01-28 | base-django-login-home          | 4.2   | completed | docs/devoluciones/12-validacion-base-django-login-home-tarea-4.2.md                |
| 2025-01-28 | base-django-login-home          | 5.1   | completed | docs/devoluciones/13-validacion-base-django-login-home-tarea-5.1.md                |
| 2025-01-28 | base-django-login-home          | 5.2   | completed | docs/devoluciones/14-validacion-base-django-login-home-tarea-5.2.md                |
| 2025-01-28 | base-django-login-home          | 5.3   | completed | docs/devoluciones/15-validacion-base-django-login-home-tarea-5.3.md                |
| 2025-01-28 | base-django-login-home          | 7.1   | completed | docs/devoluciones/16-validacion-base-django-login-home-tarea-7.1.md                |
| 2025-01-28 | base-django-login-home          | 7.2   | completed | docs/devoluciones/17-validacion-base-django-login-home-tarea-7.2.md                |
| 2025-01-28 | base-django-login-home          | 7.3   | completed | docs/devoluciones/18-validacion-base-django-login-home-tarea-7.3.md                |
| 2025-01-28 | base-django-login-home          | 7.4   | completed | docs/devoluciones/19-validacion-base-django-login-home-tarea-7.4.md                |
| 2025-01-28 | base-django-login-home          | 8.1   | completed | docs/devoluciones/20-validacion-base-django-login-home-tarea-8.1.md                |
| 2025-01-28 | base-django-login-home          | 8.2   | completed | docs/devoluciones/21-validacion-base-django-login-home-tarea-8.2.md                |
| 2025-01-28 | base-django-login-home          | 8.3   | completed | docs/devoluciones/22-validacion-base-django-login-home-tarea-8.3.md                |
| 2025-01-28 | base-django-login-home          | 10    | completed | docs/devoluciones/30-validacion-base-django-login-home-tarea-10.md                 |
| 2025-01-28 | base-django-login-home          | 11.1  | completed | docs/devoluciones/31-validacion-base-django-login-home-tarea-11.1.md               |
| 2025-01-26 | base-django-login-home          | 11.2  | completed | docs/devoluciones/32-validacion-base-django-login-home-tarea-11.2.md               |
| 2026-06-22 | base-django-login-home          | 12    | completed | docs/devoluciones/33-validacion-base-django-login-home-tarea-12.md                 |
| 2026-06-22 | usuarios-demo-perfiles-permisos | 1.1   | completed | docs/devoluciones/37-validacion-usuarios-demo-perfiles-permisos-tarea-1.1.md       |
| 2026-06-22 | usuarios-demo-perfiles-permisos | 2.1   | completed | docs/devoluciones/38-validacion-usuarios-demo-perfiles-permisos-tarea-2.1.md       |
| 2026-06-22 | usuarios-demo-perfiles-permisos | 2.2   | completed | docs/devoluciones/39-validacion-usuarios-demo-perfiles-permisos-tarea-2.2.md       |
| 2026-06-22 | usuarios-demo-perfiles-permisos | 2.3   | completed | docs/devoluciones/40-validacion-usuarios-demo-perfiles-permisos-tarea-2.3.md       |
| 2026-06-22 | usuarios-demo-perfiles-permisos | 2.4   | completed | docs/devoluciones/41-validacion-usuarios-demo-perfiles-permisos-tarea-2.4.md       |
| 2026-06-22 | usuarios-demo-perfiles-permisos | 3.1   | completed | docs/devoluciones/42-validacion-usuarios-demo-perfiles-permisos-tarea-3.1.md       |
| 2026-06-22 | usuarios-demo-perfiles-permisos | 3.2   | completed | docs/devoluciones/43a-validacion-usuarios-demo-perfiles-permisos-tarea-3.2.md      |
| 2026-06-22 | usuarios-demo-perfiles-permisos | 3.3   | completed | docs/devoluciones/43b-validacion-usuarios-demo-perfiles-permisos-tarea-3.3.md      |
| 2026-06-22 | usuarios-demo-perfiles-permisos | 4     | completed | docs/devoluciones/43-validacion-usuarios-demo-perfiles-permisos-tarea-4.md         |
| 2026-06-22 | usuarios-demo-perfiles-permisos | 5.1   | completed | docs/devoluciones/44-validacion-usuarios-demo-perfiles-permisos-tarea-5.1.md       |
| 2025-01-30 | usuarios-demo-perfiles-permisos | 5.2   | completed | docs/devoluciones/45-validacion-usuarios-demo-perfiles-permisos-tarea-5.2.md       |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 5.3   | completed | docs/devoluciones/46-validacion-usuarios-demo-perfiles-permisos-tarea-5.3.md       |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 5.4   | completed | docs/devoluciones/47-validacion-usuarios-demo-perfiles-permisos-tarea-5.4.md       |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 6     | completed | docs/devoluciones/49-kiro-validacion-usuarios-demo-perfiles-permisos-tarea-6.md    |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 7.1   | completed | docs/devoluciones/50-validacion-usuarios-demo-perfiles-permisos-tarea-7.1.md       |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 7.2   | completed | docs/devoluciones/51-validacion-usuarios-demo-perfiles-permisos-tarea-7.2.md       |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 8.1   | completed | docs/devoluciones/52-validacion-usuarios-demo-perfiles-permisos-tarea-8.1.md       |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 8.2   | completed | docs/devoluciones/53-validacion-usuarios-demo-perfiles-permisos-tarea-8.2.md       |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 8.3   | completed | docs/devoluciones/55-kiro-validacion-usuarios-demo-perfiles-permisos-tarea-8.3.md  |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 9     | completed | docs/devoluciones/56-validacion-usuarios-demo-perfiles-permisos-tarea-9.md         |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 10.1  | completed | docs/devoluciones/57-validacion-usuarios-demo-perfiles-permisos-tarea-10.1.md      |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 10.2  | completed | docs/devoluciones/58-validacion-usuarios-demo-perfiles-permisos-tarea-10.2.md      |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 10.3  | completed | docs/devoluciones/59-validacion-usuarios-demo-perfiles-permisos-tarea-10.3.md      |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 11.1  | completed | docs/devoluciones/60-validacion-usuarios-demo-perfiles-permisos-tarea-11.1.md      |
| 2026-06-23 | usuarios-demo-perfiles-permisos | 12.1  | completed | docs/devoluciones/61-validacion-usuarios-demo-perfiles-permisos-tarea-12.1.md      |
| 2026-06-25 | usuarios-demo-perfiles-permisos | 13    | completed | docs/devoluciones/62-validacion-usuarios-demo-perfiles-permisos-tarea-13.md        |
| 2026-04-17 | home-chat-orchestrator-contract | 1.1   | completed | docs/devoluciones/67-validacion-home-chat-orchestrator-contract-tarea-1.1.md       |
| 2026-06-26 | home-chat-orchestrator-contract | 1.2   | completed | docs/devoluciones/67-validacion-home-chat-orchestrator-contract-tarea-1.2.md       |
| 2026-06-26 | home-chat-orchestrator-contract | 2.1   | completed | docs/devoluciones/68-validacion-home-chat-orchestrator-contract-tarea-2.1.md       |
| 2026-06-26 | home-chat-orchestrator-contract | 2.2   | completed | docs/devoluciones/69-validacion-home-chat-orchestrator-contract-tarea-2.2.md       |
| 2026-06-26 | home-chat-orchestrator-contract | 2.3   | completed | docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md       |
| 2026-06-26 | home-chat-orchestrator-contract | 3.1   | completed | docs/devoluciones/71-validacion-home-chat-orchestrator-contract-tarea-3.1.md       |
| 2026-06-26 | home-chat-orchestrator-contract | 3.2   | completed | docs/devoluciones/72-validacion-home-chat-orchestrator-contract-tarea-3.2.md       |
| 2026-06-26 | home-chat-orchestrator-contract | 4.1   | completed | docs/devoluciones/73-validacion-home-chat-orchestrator-contract-tarea-4.1.md       |
| 2026-06-26 | home-chat-orchestrator-contract | 4.2   | completed | docs/devoluciones/74-validacion-home-chat-orchestrator-contract-tarea-4.2.md       |
| 2026-06-26 | home-chat-orchestrator-contract | 5.1   | completed | docs/devoluciones/75-validacion-home-chat-orchestrator-contract-tarea-5.1.md       |
| 2026-06-26 | home-chat-orchestrator-contract | 5.2   | completed | docs/devoluciones/76-validacion-home-chat-orchestrator-contract-tarea-5.2.md       |
| 2026-06-26 | home-chat-orchestrator-contract | 6.1   | completed | docs/devoluciones/77-validacion-home-chat-orchestrator-contract-tarea-6.1.md       |
| 2026-06-26 | home-chat-orchestrator-contract | 6.2   | completed | docs/devoluciones/78-validacion-home-chat-orchestrator-contract-tarea-6.2.md       |
| 2026-06-27 | home-chat-orchestrator-contract | 7.1   | completed | docs/devoluciones/79-validacion-home-chat-orchestrator-contract-tarea-7.1.md       |
| 2026-06-27 | home-chat-orchestrator-contract | 8.1   | completed | docs/devoluciones/80-validacion-home-chat-orchestrator-contract-tarea-8.1.md       |
| 2026-06-27 | home-chat-orchestrator-contract | 8.2   | completed | docs/devoluciones/81-validacion-home-chat-orchestrator-contract-tarea-8.2.md       |
| 2026-06-27 | home-chat-orchestrator-contract | 8.3   | completed | docs/devoluciones/82-validacion-home-chat-orchestrator-contract-tarea-8.3.md       |
| 2026-06-27 | home-chat-orchestrator-contract | 8.4   | completed | docs/devoluciones/83-validacion-home-chat-orchestrator-contract-tarea-8.4.md       |
| 2026-06-27 | home-chat-orchestrator-contract | 8.5   | completed | docs/devoluciones/84-validacion-home-chat-orchestrator-contract-tarea-8.5.md       |
| 2026-04-17 | home-chat-orchestrator-contract | 8.6   | completed | docs/devoluciones/85-validacion-home-chat-orchestrator-contract-tarea-8.6.md       |
| 2026-06-27 | home-chat-orchestrator-contract | 8.7   | completed | docs/devoluciones/86-validacion-home-chat-orchestrator-contract-tarea-8.7.md       |
| 2026-04-30 | home-chat-orchestrator-contract | 8.8   | completed | docs/devoluciones/87-validacion-home-chat-orchestrator-contract-tarea-8.8.md       |
| 2026-06-27 | home-chat-orchestrator-contract | 9.1   | completed | docs/devoluciones/88-validacion-home-chat-orchestrator-contract-tarea-9.1.md       |
| 2026-06-27 | home-chat-orchestrator-contract | 10.1  | completed | docs/devoluciones/89-validacion-home-chat-orchestrator-contract-tarea-10.1.md      |
| 2026-06-27 | home-chat-orchestrator-contract | 11.1  | completed | docs/devoluciones/90-validacion-home-chat-orchestrator-contract-tarea-11.1.md      |
| 2026-06-27 | home-chat-orchestrator-contract | 11.2  | completed | docs/devoluciones/90-validacion-home-chat-orchestrator-contract-tarea-11.2.md      |
| 2026-06-27 | home-chat-orchestrator-contract | 11.3  | completed | docs/devoluciones/92-validacion-home-chat-orchestrator-contract-tarea-11.3.md      |
| 2026-06-27 | home-chat-orchestrator-contract | 11.4  | completed | docs/devoluciones/93-validacion-home-chat-orchestrator-contract-tarea-11.4.md      |
| 2026-06-27 | home-chat-orchestrator-contract | 11.5  | completed | docs/devoluciones/94-validacion-home-chat-orchestrator-contract-tarea-11.5.md      |
| 2026-06-27 | home-chat-orchestrator-contract | 12.1  | completed | docs/devoluciones/95-validacion-home-chat-orchestrator-contract-tarea-12.1.md      |
| 2026-06-27 | home-chat-orchestrator-contract | 12.2  | completed | docs/devoluciones/96-validacion-home-chat-orchestrator-contract-tarea-12.2.md      |
| 2026-06-27 | home-chat-orchestrator-contract | 12.3  | completed | docs/devoluciones/97-validacion-home-chat-orchestrator-contract-tarea-12.3.md      |
| 2026-06-27 | home-chat-orchestrator-contract | 13.1  | completed | docs/devoluciones/99-validacion-home-chat-orchestrator-contract-tarea-13.1.md      |
| 2026-06-27 | acciones-trazabilidad-metricas  | 1.1   | completed | docs/devoluciones/103-validacion-acciones-trazabilidad-metricas-tarea-1.1.md       |
| 2026-06-28 | acciones-trazabilidad-metricas  | 1.2   | completed | docs/devoluciones/104-validacion-acciones-trazabilidad-metricas-tarea-1.2.md       |
| 2026-06-28 | acciones-trazabilidad-metricas  | 1.3   | completed | docs/devoluciones/105-validacion-acciones-trazabilidad-metricas-tarea-1.3.md       |
| 2026-04-17 | acciones-trazabilidad-metricas  | 3.1   | completed | docs/devoluciones/107-validacion-acciones-trazabilidad-metricas-tarea-3.1.md       |
| 2026-04-17 | acciones-trazabilidad-metricas  | 3.2   | completed | docs/devoluciones/108-validacion-acciones-trazabilidad-metricas-tarea-3.2.md       |
| 2026-06-28 | acciones-trazabilidad-metricas  | 3.3   | completed | docs/devoluciones/109-validacion-acciones-trazabilidad-metricas-tarea-3.3.md       |
| 2026-06-28 | acciones-trazabilidad-metricas  | 4     | completed | docs/devoluciones/110-validacion-acciones-trazabilidad-metricas-tarea-4.md         |
| 2026-06-28 | acciones-trazabilidad-metricas  | 5.1   | completed | docs/devoluciones/111-validacion-acciones-trazabilidad-metricas-tarea-5.1-5.2.md   |
| 2026-06-28 | acciones-trazabilidad-metricas  | 5.2   | completed | docs/devoluciones/111-validacion-acciones-trazabilidad-metricas-tarea-5.1-5.2.md   |
| 2026-06-28 | acciones-trazabilidad-metricas  | 6     | completed | docs/devoluciones/112-validacion-acciones-trazabilidad-metricas-tarea-6.md         |
| 2026-06-28 | acciones-trazabilidad-metricas  | 7     | completed | docs/devoluciones/113-validacion-acciones-trazabilidad-metricas-tarea-7.md         |
| 2026-06-28 | acciones-trazabilidad-metricas  | 8     | completed | docs/devoluciones/114-validacion-acciones-trazabilidad-metricas-tarea-8.md         |
| 2026-06-30 | acciones-trazabilidad-metricas  | 9.1   | completed | docs/devoluciones/115-validacion-acciones-trazabilidad-metricas-tarea-9.1.md       |
| 2026-06-30 | acciones-trazabilidad-metricas  | 9.2   | completed | docs/devoluciones/116-validacion-acciones-trazabilidad-metricas-tarea-9.2.md       |
| 2026-06-30 | acciones-trazabilidad-metricas  | 9.3   | completed | docs/devoluciones/117-validacion-acciones-trazabilidad-metricas-tarea-9.3.md       |
| 2026-06-30 | acciones-trazabilidad-metricas  | 9.4   | completed | docs/devoluciones/118-validacion-acciones-trazabilidad-metricas-tarea-9.4.md       |
| 2026-06-30 | acciones-trazabilidad-metricas  | 9.5   | completed | docs/devoluciones/119-validacion-acciones-trazabilidad-metricas-tarea-9.5.md       |
| 2026-06-30 | acciones-trazabilidad-metricas  | 10    | completed | docs/devoluciones/120-validacion-acciones-trazabilidad                             |
| 2026-07-01 | acciones-trazabilidad-metricas  | 11.1  | completed | docs/devoluciones/121-validacion-acciones-trazabilidad-metricas-tarea-11.1.md      |
| 2026-07-01 | acciones-trazabilidad-metricas  | 11.2  | completed | docs/devoluciones/122-validacion-acciones-trazabilidad-metricas-tarea-11.2.md      |
| 2026-07-01 | acciones-trazabilidad-metricas  | 12.1  | completed | docs/devoluciones/123-validacion-acciones-trazabilidad-metricas-tarea-12.1.md      |
| 2026-07-01 | acciones-trazabilidad-metricas  | 12.2  | completed | docs/devoluciones/124-validacion-acciones-trazabilidad-metricas-tarea-12.2.md      |
| 2026-07-01 | acciones-trazabilidad-metricas  | 12.3  | completed | docs/devoluciones/125-validacion-acciones-trazabilidad-metricas-tarea-12.3.md      |
| 2026-07-01 | acciones-trazabilidad-metricas  | 13.1  | completed | docs/devoluciones/127-validacion-acciones-trazabilidad-metricas-tarea-13.1.md      |
| 2026-07-01 | acciones-trazabilidad-metricas  | 14.1  | completed | docs/devoluciones/128-validacion-acciones-trazabilidad-metricas-tarea-14.1.md      |
| 2026-07-01 | acciones-trazabilidad-metricas  | 14.2  | completed | docs/devoluciones/130-validacion-acciones-trazabilidad-metricas-tarea-14.2-kiro.md |
| 2026-07-01 | acciones-trazabilidad-metricas  | 15    | completed | docs/devoluciones/131-validacion-acciones-trazabilidad-metricas-tarea-15-kiro.md   |

---

## Notas

- base-django-login-home completado — todas las 12 tareas validadas
- usuarios-demo-perfiles-permisos completado — todas las 13 tareas validadas
- home-chat-orchestrator-contract completado — todas las 13 tareas validadas (incluyendo 6 sub-tareas MANDATORY de testing)
- acciones-trazabilidad-metricas **completado** — todas las tareas (1.1–14.2 + 15 checkpoint final) validadas. Gap Req 7 AC2 / 2.3 / 2.7 resuelto en tarea 15 (Opción 2, aprobado): 'running' + detected_intention/selection_reason/permissions_applied preparados pero no poblados en MVP 1 (la clasificación la hace n8n). Documentado en requirements.md (Decision 7) y design.md.
- Próximo: rag-mails-dataset-permissions (Paso 3.1 requirements). Dependencias completed. Puede ir en paralelo con trigger-comunicaciones-email.
