# Validación — Tarea 12.1: Write integration tests for /api/actions/

**Spec:** acciones-trazabilidad-metricas
**Fecha:** 2026-07-01
**Tarea:** 12.1 — "Write integration tests for /api/actions/ in core/tests.py (módulo
único; ver docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md
— mismo criterio que 11.x)"

---

## Qué se validó

Se agregaron 3 integration tests para `GET /api/actions/` como clase nueva
`ApiActionsIntegrationTest` en `app/core/tests.py` (líneas 1750–1821), después de
`MetricsAggregatorTest`, siguiendo el mismo módulo único ya establecido en devoluciones
previas (70, 121, 122).

**Método:** `TestCase` estándar de Django con `self.client`, sin mocks — se ejercitan
`TraceabilityManager.create_run` (para poblar `WorkflowRun` reales) y la vista
`api_actions` (`app/core/views.py:275-323`) contra la base de datos de test, con dos
usuarios de prueba (`perfil='Usuario'`) creados en `setUp`.

Durante la implementación se detectó un criterio fallido preexistente (ver "Cambio
adicional" abajo) que requirió modificar `app/core/views.py`.

---

## Resultados por criterio de tasks.md

| Criterio (tasks.md, tarea 12.1) | Estado | Evidencia |
|---|---|---|
| `test_api_actions_returns_only_user_runs`: create 2 users with runs, verify user1 only sees their own runs | Cumplido | `app/core/tests.py:1775-1797`. Crea `user1` y `user2` (perfil Usuario), un `WorkflowRun` para cada uno vía `TraceabilityManager.create_run`. Autentica como `user1` (`self.client.force_login`), hace `GET /api/actions/`. Asserts: `response.status_code == 200`, `data['count'] == 1`, el `id` del run de `user1` está en `data['results']` (el de `user2` no aparece, ya que `count == 1`). Test pasa. |
| `test_api_actions_requires_authentication`: verify HTTP 401 when not authenticated | Cumplido | `app/core/tests.py:1799-1802`. `GET /api/actions/` sin login. Assert: `response.status_code == 401`. Test pasa — requirió el cambio de código documentado en "Cambio adicional" (antes del fix, la vista devolvía 302, no 401). |
| `test_api_actions_paginates_results`: create 25 runs, verify response has 20 items and next link | Cumplido | `app/core/tests.py:1804-1821`. Crea 25 `WorkflowRun` para `user1`, autentica, `GET /api/actions/` (page_size default=20). Asserts: `len(data['results']) == 20`, `data['next']` no es `None`. Test pasa. |
| Requirements referenciados: 4.2, 4.5, 4.6 | Cumplido | 4.2 (solo se retornan acciones del usuario autenticado) cubierto por `test_api_actions_returns_only_user_runs`; 4.5 (paginación 20/página con `next`) cubierto por `test_api_actions_paginates_results`; 4.6 (HTTP 401 si no autenticado) cubierto por `test_api_actions_requires_authentication`, y solo se cumple después del cambio adicional descrito abajo. |

**Evidencia de ejecución:**

- `python -Wa manage.py test core.tests.ApiActionsIntegrationTest -v 2` → **3/3 tests, OK**
- `python -Wa manage.py test core.tests.ChatViewIntegrationTest core.tests.TraceabilityManagerTest core.tests.MetricsAggregatorTest -v 2` → **14/14 tests, OK** (corrida específica para confirmar que el cambio del decorador no rompió `chat_view` — su test `test_unauthenticated_user_gets_redirect` sigue esperando 302, y sigue pasando, porque `chat_view` no fue tocado).
- `python -Wa manage.py test` (suite completa) → **132/132 tests, OK** — sube desde 129
  (devolución 122) a 132, es decir +3, exactamente los tests nuevos de esta tarea. Ningún
  test preexistente se rompió (corrida completa, incluye tests property-based con
  Hypothesis; tardó ~523s).

Nota sobre variables de entorno: para correr `manage.py test` se exportaron valores
descartables (`DJANGO_SECRET_KEY=test-only-secret-key`,
`DATABASE_URL=sqlite:///db.sqlite3`, `N8N_WEBHOOK_URL=...localhost:5678...`) únicamente
en la subshell del comando de test, sin leer ni mostrar el `.env` real en ningún momento
— cumple con la restricción de `security-permissions.md`.

---

## Cambio adicional

**Bug detectado:** `api_actions` (y, por el mismo patrón, `api_action_detail`,
`api_metrics`, `api_admin_actions`) usaban `@login_required` de Django, que **redirige
(302)** a `/login/` para requests no autenticados. Requirement 4.6 exige explícitamente
`HTTP 401` para `/api/actions/` sin autenticar, y el propio criterio de aceptación de la
tarea 12.1 lo pedía como test (`test_api_actions_requires_authentication`). Antes del
fix, ese test fallaba (302 ≠ 401).

**Fix aplicado:** se agregó un decorador `api_login_required` en `app/core/views.py`
(líneas 33-42) que responde `JsonResponse({'error': 'Autenticación requerida'},
status=401)` en vez de redirigir cuando `request.user.is_authenticated` es `False`. Se
reemplazó `@login_required` por `@api_login_required` en los 4 endpoints `/api/*` de
este spec:

- `api_actions` (línea 275)
- `api_action_detail` (línea 327)
- `api_metrics` (línea 349)
- `api_admin_actions` (línea 388)

**No se tocó:**
- `actions_page` (línea 455, ruta `/actions/`): sigue con `@login_required` — es una
  vista de página, no de API, y el redirect a `/login/` es el comportamiento correcto
  (así lo confirma su propio criterio en Requirement 6.7 / tarea 9.4, y no forma parte
  del alcance ni de los requirements de esta tarea).
- `chat_view` (ruta `/api/chat/`): pertenece al spec `home-chat-orchestrator-contract`,
  no a `acciones-trazabilidad-metricas`, y ya tiene un test validado
  (`test_unauthenticated_user_gets_redirect`) que espera 302. Modificarlo estaba fuera
  del alcance de esta tarea y de este spec.

**Justificación:** decisión consultada y confirmada explícitamente por el usuario antes
de implementar (ver conversación de planificación): Requirement 4.6 pide 401 de forma
explícita, y la semántica correcta para un endpoint `/api/*` es devolver un error JSON,
no redirigir a una página HTML — el 302 es comportamiento de vista de página, no de API.

**Impacto en otros tests:** ninguno. Se corrieron explícitamente `ChatViewIntegrationTest`
(incluye el test que depende de 302 en `/api/chat/`), `TraceabilityManagerTest` y
`MetricsAggregatorTest`, y la suite completa (132 tests) — todos pasan.

---

## Alcance respetado

- Se tocó `app/core/views.py` (decorador nuevo + 4 reemplazos de decorador, sin cambiar
  lógica interna de las vistas) y `app/core/tests.py` (clase nueva al final del archivo).
- No se tocó `core/services.py`, `core/models.py`, `tasks.md` ni ningún otro archivo.
- No se implementó ninguna otra tarea (12.2, 12.3, 13.x, 14.x quedan pendientes).
- No se rediseñaron templates, no se renombró el producto, no se inventaron endpoints
  nuevos (el decorador solo cambia el tipo de respuesta ante falta de autenticación en
  endpoints ya existentes de este spec).
- No se leyó ni se mostró contenido de `.env` real en ningún momento.

## Veredicto

Pendiente de validación por Kiro contra `requirements.md` y `tasks.md`. No se marca la
tarea 12.1 como completed en este documento ni se realiza commit todavía, conforme al
protocolo de CLAUDE.md.
