# Validación — usuarios-demo-perfiles-permisos / Tarea 8.3

**Fecha:** 2026-06-23
**Spec:** usuarios-demo-perfiles-permisos
**Tarea:** 8.3 — Write integration test para load_demo_users end-to-end
**Veredicto:** Pendiente de validación Kiro

---

## Qué se implementó

Se agregó la clase `LoadDemoUsersIntegrationTest(TestCase)` al final de `app/core/tests.py`, con 5 integration tests end-to-end para el comando `load_demo_users`.

También se agregaron 6 imports nuevos al inicio del archivo:
`json`, `os`, `tempfile`, `StringIO`, `call_command`, `CommandError`.

---

## Archivos modificados

- `app/core/tests.py` — imports (líneas 1-6 nuevas) + clase `LoadDemoUsersIntegrationTest` (al final)

---

## Criterios de aceptación vs. resultado

| Criterio | Estado | Evidencia |
|---|---|---|
| Test carga exitosa desde fixture demo_users.json | ✅ cumplido | `test_load_from_fixture_creates_100_users`: llama `call_command('load_demo_users', fixture=FIXTURE_PATH)` y verifica `CoreUser.objects.count() == 100`. Output: `ok` |
| Test validación de 12 usuarios específicos después de carga | ✅ cumplido | `test_12_specific_users_present_after_load`: carga fixture y verifica `first_name`, `last_name`, `perfil` de los 12 usuarios específicos con `subTest`. Output: `ok` |
| Test dry-run no crea usuarios | ✅ cumplido | `test_dry_run_does_not_create_users`: llama con `dry_run=True` y verifica `CoreUser.objects.count() == 0`. Output: `ok` |
| Test rechazo de fixture con usuario faltante | ✅ cumplido | `test_reject_fixture_with_missing_required_user`: crea fixture sin `comustock.ci@gmail.com` en tempfile, verifica `assertRaises(CommandError)`. Output: `ok` |
| Test rechazo de fixture con email duplicado | ✅ cumplido | `test_reject_fixture_with_duplicate_email`: crea fixture con entrada duplicada (pk=9999, mismo email), verifica `assertRaises(CommandError)`. Output: `ok` |

---

## Ejecución de tests

```
python3 -Wa manage.py test core.tests.LoadDemoUsersIntegrationTest -v 2

test_12_specific_users_present_after_load ... ok
test_dry_run_does_not_create_users ... ok
test_load_from_fixture_creates_100_users ... ok
test_reject_fixture_with_duplicate_email ... ok
test_reject_fixture_with_missing_required_user ... ok

Ran 5 tests in 0.458s
OK
```

**Suite completa (sin regresiones):**
```
Ran 38 tests in 488.067s
OK
```

38 tests = 33 existentes + 5 nuevos de esta tarea.

---

## Requirements cubiertos

- Requirement 7.2: carga desde fixture JSON — validado por `test_load_from_fixture_creates_100_users`
- Requirement 7.3: valida 12 usuarios específicos — validado por `test_12_specific_users_present_after_load`
- Requirement 7.4: total 100 usuarios — implícito en test de carga exitosa
- Requirement 7.6: rechazo con mensaje descriptivo — validado por tests de `CommandError`
