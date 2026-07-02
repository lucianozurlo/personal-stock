# Validación — Tarea 12.3: Write integration tests for /api/admin/actions/

**Spec:** acciones-trazabilidad-metricas
**Fecha:** 2026-07-01
**Tarea:** 12.3 — "Write integration tests for /api/admin/actions/ in core/tests.py
(módulo único; ver docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md
— mismo criterio que 11.x)"

---

## Qué se validó

Se agregaron 3 integration tests para `GET /api/admin/actions/` como clase nueva
`ApiAdminActionsIntegrationTest` en `app/core/tests.py` (líneas 1936-2034), inmediatamente
después de `ApiMetricsIntegrationTest`, siguiendo el mismo módulo único ya establecido en
devoluciones previas (70, 121, 122, 123, 124).

**Método:** `TestCase` estándar de Django con `self.client`, sin mocks — se ejercitan
`TraceabilityManager.create_run` (para poblar `WorkflowRun` reales) y la vista
`api_admin_actions` (`app/core/views.py:388-450`) contra la base de datos de test.
`setUp` crea 4 usuarios: dos con `perfil=CoreUser.Profile.USUARIO` (para los runs a
listar), uno con `perfil=CoreUser.Profile.ADMINISTRADOR` (para autenticar contra el
endpoint) y uno con `perfil=CoreUser.Profile.USUARIO_IC` (para el caso 403), usando las
constantes `TextChoices` del modelo `User` (nunca strings literales), tal como exige el
criterio CRITICAL de la tarea y `design.md` (sección "Uso de Constantes de Perfil").

No se detectó ningún bug durante la implementación — `api_admin_actions`,
`PermissionChecker.can_access_admin_actions` y
`PermissionChecker.get_all_runs_queryset` ya estaban implementados correctamente (tareas
3.3, 7.3) y no requirieron cambios.

---

## Resultados por criterio de tasks.md

| Criterio (tasks.md, tarea 12.3) | Estado | Evidencia |
|---|---|---|
| `test_api_admin_actions_requires_administrador`: create Usuario IC user, verify HTTP 403 | Cumplido | `app/core/tests.py:1976-1983`. Crea usuario con `perfil=CoreUser.Profile.USUARIO_IC`, autentica (`force_login`), hace `GET /api/admin/actions/`. Asserts: `response.status_code == 403`, `'error' in data`. Test pasa. |
| `test_api_admin_actions_returns_all_users_runs`: create 2 users with runs, authenticate as Administrador, verify response contains runs from both users | Cumplido | `app/core/tests.py:1985-2010`. Crea 1 `WorkflowRun` para `user1` y 1 para `user2` vía `TraceabilityManager.create_run`. Autentica como Administrador, `GET /api/admin/actions/` (sin `user_id`). Asserts: `status_code == 200`, `data['count'] == 2`, ambos `run1.id` y `run2.id` presentes en `data['results']`. Test pasa. |
| `test_api_admin_actions_filters_by_user_id`: verify response only contains runs for specified user_id | Cumplido | `app/core/tests.py:2012-2034`. Crea 1 run para `user1` y 1 para `user2`. Autentica como Administrador, `GET /api/admin/actions/?user_id=<user1.id>`. Asserts: `status_code == 200`, `data['count'] == 1`, `data['results'][0]['id'] == run1.id`, `data['results'][0]['user_id'] == user1.id` (verifica que NO se filtró el run de user2). Test pasa. |
| **CRITICAL**: Use `User.Profile.ADMINISTRADOR` constant in test setup and assertions, NOT literal string | Cumplido | `app/core/tests.py:1943, 1950, 1957, 1964` (setUp). Usa `CoreUser.Profile.USUARIO` (x2), `CoreUser.Profile.ADMINISTRADOR` y `CoreUser.Profile.USUARIO_IC`. Ningún string literal `'Administrador'`/`'Usuario'`/`'Usuario IC'` se usó para comparaciones o creación de perfil en esta clase. |
| Requirements referenciados: 10.2, 10.4, 10.5 | Cumplido | 10.2 (perfil distinto de Administrador → 403) cubierto por `test_api_admin_actions_requires_administrador`; 10.4 (sin `user_id` → acciones de todos los usuarios) cubierto por `test_api_admin_actions_returns_all_users_runs`; 10.5 (formato de respuesta igual a `/api/actions/` + campos adicionales como `user_id`) verificado indirectamente al comprobar `data['results'][0]['user_id']` en el test de filtro — el campo `user_id` solo existe en la respuesta de `/api/admin/actions/`, no en `/api/actions/` (Req 10.6). |

**Evidencia de ejecución:**

- `python -Wa manage.py test core.tests.ApiAdminActionsIntegrationTest -v 2` → **3/3 tests, OK**
- `python -Wa manage.py test` (suite completa) → **138/138 tests, OK** — sube desde 135
  (devolución 124) a 138, es decir +3, exactamente los tests nuevos de esta tarea. Ningún
  test preexistente se rompió (corrida completa, incluye tests property-based con
  Hypothesis; tardó ~532s).

Nota sobre variables de entorno: para correr `manage.py test` se activó el virtualenv del
proyecto (`.venv`) y se cargaron las variables ya declaradas en el `.env` real
(`source .env` en subshell, sin leer ni mostrar su contenido en la conversación) — cumple
con la restricción de `security-permissions.md` de no mostrar el contenido del `.env`
real.

---

## Cambio adicional

Ninguno. No se detectaron bugs ni criterios fallidos durante la implementación —
`api_admin_actions`, `PermissionChecker.can_access_admin_actions` y
`PermissionChecker.get_all_runs_queryset` ya funcionaban según lo especificado en
`design.md` y `requirements.md` (tareas 3.3 y 7.3, ya validadas en devoluciones
anteriores).

---

## Alcance respetado

- Se tocó únicamente `app/core/tests.py` (clase nueva `ApiAdminActionsIntegrationTest` al
  final del archivo).
- No se tocó `core/views.py`, `core/services.py`, `core/models.py`, `core/urls.py`,
  `tasks.md` ni ningún otro archivo.
- No se implementó ninguna otra tarea (13.x, 14.x, 15 quedan pendientes).
- No se rediseñaron templates, no se renombró el producto, no se inventaron endpoints
  nuevos.
- No se leyó ni se mostró contenido del `.env` real en ningún momento.

## Veredicto

Pendiente de validación por Kiro contra `requirements.md` y `tasks.md`. No se marca la
tarea 12.3 como completed en este documento ni se realiza commit todavía, conforme al
protocolo de CLAUDE.md.
