# Validación: usuarios-demo-perfiles-permisos — Tarea 6

**Spec:** usuarios-demo-perfiles-permisos  
**Tarea:** 6 — Checkpoint - Validar DatasetFilter  
**Fecha:** 2026-06-23  
**Veredicto propuesto:** COMPLETED

---

## Qué se validó

Checkpoint de verificación de la implementación de DatasetFilter (tareas 5.1–5.4):
- Clase `DatasetFilter` en `app/core/permissions.py`
- Property tests (Properties 5 y 6) usando Hypothesis
- Unit tests de edge cases
- Performance test con dataset real

Comando ejecutado:
```bash
cd app && DJANGO_SECRET_KEY='django-insecure-test-key-for-ci-only-not-production' \
  DATABASE_URL='sqlite:///db.sqlite3' \
  python3 -Wa manage.py test core --verbosity=2
```

---

## Resultado del test runner

```
Found 24 test(s).
Ran 24 tests in 461.486s
OK
System check identified no issues (0 silenced).
```

**Exit code: 0. 0 errores. 0 failures.**

---

## Tests de DatasetFilter ejecutados (12 de 24 totales)

| Test | Descripción | Resultado |
|------|-------------|-----------|
| `DatasetFilterPerformanceTest.test_performance_filter_under_50ms` | Filtro < 50ms con dataset real | OK |
| `DatasetFilterPropertyTest.test_property_5_filtering_restricted_substrings` | Property 5: substrings restringidas → excluidas para Usuario | OK |
| `DatasetFilterPropertyTest.test_property_6_access_privileged_profiles` | Property 6: perfiles privilegiados acceden a todo | OK |
| `DatasetFilterUnitTest.test_case_insensitive_macro_lowercase` | `macro` (minúsculas) → excluido para Usuario | OK |
| `DatasetFilterUnitTest.test_case_insensitive_macro_mixed` | `Macro` (mixto) → excluido para Usuario | OK |
| `DatasetFilterUnitTest.test_case_insensitive_macro_uppercase` | `MACRO` (mayúsculas) → excluido para Usuario | OK |
| `DatasetFilterUnitTest.test_destinatario_empty_includes_record` | `destinatario=''` → incluir registro | OK |
| `DatasetFilterUnitTest.test_destinatario_missing_includes_record` | sin campo destinatario → incluir registro | OK |
| `DatasetFilterUnitTest.test_destinatario_none_includes_record` | `destinatario=None` → incluir registro | OK |
| `DatasetFilterUnitTest.test_empty_dataset_returns_empty_list` | dataset vacío → lista vacía | OK |
| `DatasetFilterUnitTest.test_user_empty_perfil_raises_value_error` | `perfil=''` → ValueError | OK |
| `DatasetFilterUnitTest.test_user_none_raises_value_error` | `user=None` → ValueError | OK |

---

## Criterios de la tarea 6 — evaluación punto por punto

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| Ejecutar todos los tests de DatasetFilter | Cumplido | 12 tests DatasetFilter ejecutados, todos OK (ver tabla arriba) |
| Verificar que filtro excluye correctamente contenido restringido | Cumplido | Property 5 (100 ejemplos Hypothesis) + 3 unit tests case-insensitive (MACRO/Macro/macro) = OK |
| Verificar que perfiles privilegiados acceden a todo | Cumplido | Property 6 (100 ejemplos Hypothesis, perfiles: Administrador/Usuario IC/Heavy user/Macro) = OK |
| Reportar resultados punto por punto | Cumplido | Este documento |

---

## Hallazgos adicionales

- 24/24 tests de la suite completa también pasaron (tests de auth, configuración, roles, usuarios)
- Performance: el filtro no excedió 50ms con el dataset real (Requirement 10.3)
- Ningún bug detectado. No hubo correcciones adicionales.
