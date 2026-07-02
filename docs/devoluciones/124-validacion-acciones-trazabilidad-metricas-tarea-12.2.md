# Validación — Tarea 12.2: Write integration tests for /api/metrics/

**Spec:** acciones-trazabilidad-metricas
**Fecha:** 2026-07-01
**Tarea:** 12.2 — "Write integration tests for /api/metrics/ in core/tests.py (módulo
único; ver docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md
— mismo criterio que 11.x)"

---

## Qué se validó

Se agregaron 3 integration tests para `GET /api/metrics/` como clase nueva
`ApiMetricsIntegrationTest` en `app/core/tests.py` (líneas 1826-1930), después de
`ApiActionsIntegrationTest`, siguiendo el mismo módulo único ya establecido en
devoluciones previas (70, 121, 122, 123).

**Método:** `TestCase` estándar de Django con `self.client`, sin mocks — se ejercitan
`TraceabilityManager.create_run` / `complete_run` / `fail_run` (para poblar
`WorkflowRun` reales) y la vista `api_metrics` (`app/core/views.py:349-385`) contra la
base de datos de test. `setUp` crea dos usuarios: uno con `perfil=CoreUser.Profile.USUARIO`
y otro con `perfil=CoreUser.Profile.ADMINISTRADOR`, usando las constantes `TextChoices`
del modelo `User` (nunca strings literales), tal como exige el criterio CRITICAL de la
tarea y `design.md` (sección "Uso de Constantes de Perfil").

No se detectó ningún bug durante la implementación — `api_metrics`, `PermissionChecker` y
`MetricsAggregator` ya estaban implementados correctamente (tareas 3.2, 3.3, 7.2) y no
requirieron cambios.

---

## Resultados por criterio de tasks.md

| Criterio (tasks.md, tarea 12.2) | Estado | Evidencia |
|---|---|---|
| `test_api_metrics_requires_privileged_profile`: create Usuario user, verify HTTP 403 | Cumplido | `app/core/tests.py:1850-1856`. Crea usuario con `perfil=CoreUser.Profile.USUARIO`, autentica (`force_login`), hace `GET /api/metrics/`. Asserts: `response.status_code == 403`, `'error' in data`. Test pasa. |
| `test_api_metrics_allows_administrador`: create Administrador user, verify HTTP 200 | Cumplido | `app/core/tests.py:1859-1864`. Autentica con usuario `perfil=CoreUser.Profile.ADMINISTRADOR`, `GET /api/metrics/`. Assert: `response.status_code == 200`. Test pasa. |
| `test_api_metrics_returns_aggregated_data`: create runs with different agents/states, verify response structure | Cumplido | `app/core/tests.py:1866-1918`. Crea 3 `WorkflowRun`: 2 con agente `rag-mails` (uno `completed` vía `complete_run`, otro `failed` vía `fail_run`) y 1 con agente `trigger-comunicaciones` (`completed`). Autentica como Administrador, `GET /api/metrics/`. Asserts: `status_code == 200`; las 5 claves (`total_executions`, `executions_by_agent`, `executions_by_state`, `avg_execution_time_ms`, `error_rate`) están presentes; `total_executions == 3`; `executions_by_agent['rag-mails'] == 2`, `['trigger-comunicaciones'] == 1`; `executions_by_state['completed'] == 2`, `['failed'] == 1`; `error_rate['rag-mails'] == 0.5`, `['trigger-comunicaciones'] == 0.0`. Test pasa. |
| **CRITICAL**: Use `User.Profile.ADMINISTRADOR` and `User.Profile.USUARIO_IC` constants in test assertions, NOT literal strings | Cumplido | `app/core/tests.py:1839, 1847`. `setUp` usa `CoreUser.Profile.USUARIO` y `CoreUser.Profile.ADMINISTRADOR` (alias `CoreUser` ya apunta a `core.models.User`, importado en la línea 19 del archivo). No se usó ningún string literal `'Administrador'`/`'Usuario'` para las comparaciones de perfil en esta clase. (Nota: la tarea no requirió `USUARIO_IC` porque el criterio de aceptación solo pide los casos Usuario→403 y Administrador→200; se mantuvo el alcance exacto de 12.2.) |
| Requirements referenciados: 5.2, 5.3, 5.5 | Cumplido | 5.2 (perfiles no privilegiados → 403) cubierto por `test_api_metrics_requires_privileged_profile`; 5.3 (métricas agregadas: total, por agente, por estado, tiempo promedio, error rate) cubierto por `test_api_metrics_returns_aggregated_data`; 5.5 (JSON con nombres de campo claros) verificado explícitamente comprobando las 5 claves del response. |

**Evidencia de ejecución:**

- `python -Wa manage.py test core.tests.ApiMetricsIntegrationTest -v 2` → **3/3 tests, OK**
- `python -Wa manage.py test` (suite completa) → **135/135 tests, OK** — sube desde 132
  (devolución 123) a 135, es decir +3, exactamente los tests nuevos de esta tarea. Ningún
  test preexistente se rompió (corrida completa, incluye tests property-based con
  Hypothesis; tardó ~522s).

Nota sobre variables de entorno: para correr `manage.py test` se cargaron las variables
ya declaradas en el `.env` real del proyecto (`source .env` en subshell, sin leer ni
mostrar su contenido en la conversación) — cumple con la restricción de
`security-permissions.md` de no mostrar el contenido del `.env` real.

---

## Cambio adicional

Ninguno. No se detectaron bugs ni criterios fallidos durante la implementación —
`api_metrics`, `PermissionChecker.can_access_metrics` y
`MetricsAggregator.get_summary_metrics` ya funcionaban según lo especificado en
`design.md` y `requirements.md` (tareas 3.2, 3.3 y 7.2, ya validadas en devoluciones
anteriores).

---

## Alcance respetado

- Se tocó únicamente `app/core/tests.py` (clase nueva `ApiMetricsIntegrationTest` al
  final del archivo).
- No se tocó `core/views.py`, `core/services.py`, `core/models.py`, `core/urls.py`,
  `tasks.md` ni ningún otro archivo.
- No se implementó ninguna otra tarea (12.3, 13.x, 14.x quedan pendientes).
- No se rediseñaron templates, no se renombró el producto, no se inventaron endpoints
  nuevos.
- No se leyó ni se mostró contenido del `.env` real en ningún momento.

## Veredicto

Pendiente de validación por Kiro contra `requirements.md` y `tasks.md`. No se marca la
tarea 12.2 como completed en este documento ni se realiza commit todavía, conforme al
protocolo de CLAUDE.md.
