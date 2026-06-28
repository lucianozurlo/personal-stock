# Validación — usuarios-demo-perfiles-permisos — Tarea 5.3

**Spec:** usuarios-demo-perfiles-permisos
**Tarea:** 5.3 — Write unit tests for DatasetFilter edge cases
**Fecha:** 2026-06-23
**Veredicto:** ✅ **COMPLETED**

---

## Qué se implementó

Se agregó la clase `DatasetFilterUnitTest(TestCase)` en `app/core/tests.py` con 9 unit tests deterministas para casos borde del `DatasetFilter`.

Se corrigió además un bug en `app/core/permissions.py` (líneas 39 y 64): cuando el campo `destinatario` existe en el registro pero su valor es `None` (no ausente), `record.get('destinatario', '').lower()` retornaba `None` en lugar del string vacío y lanzaba `AttributeError`. El fix: `(record.get('destinatario') or '').lower()`.

---

## Archivos modificados

| Archivo                   | Cambio                                                              |
| ------------------------- | ------------------------------------------------------------------- |
| `app/core/tests.py`       | Agregada clase `DatasetFilterUnitTest` con 9 tests (líneas 300–378) |
| `app/core/permissions.py` | Fix `None`-destinatario en líneas 39 y 64                           |

---

## Criterios de aceptación — verificación punto por punto

| Criterio (tasks.md 5.3)                                       | Estado   | Evidencia                                                                                                                                   |
| ------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Test con usuario sin perfil definido → debe lanzar ValueError | Cumplido | `test_user_none_raises_value_error` y `test_user_empty_perfil_raises_value_error` — ambos OK                                                |
| Test con dataset vacío → debe retornar lista vacía            | Cumplido | `test_empty_dataset_returns_empty_list` — OK                                                                                                |
| Test con destinatario None o vacío → debe incluir registro    | Cumplido | `test_destinatario_none_includes_record`, `test_destinatario_empty_includes_record`, `test_destinatario_missing_includes_record` — todos OK |
| Test case-insensitive matching (MACRO, Macro, macro)          | Cumplido | `test_case_insensitive_macro_uppercase`, `test_case_insensitive_macro_mixed`, `test_case_insensitive_macro_lowercase` — todos OK            |
| Requirements 5.5, 10.1 cubiertos                              | Cumplido | Cada test documenta el Req que valida en su docstring                                                                                       |

---

## Resultado de ejecución

```
python3 -Wa manage.py test core.tests.DatasetFilterUnitTest -v 2

Ran 9 tests in 9.214s
OK
```

```
python3 -Wa manage.py test -v 1  (suite completa)

Ran 23 tests in 541.827s
OK
```

Sin regresiones. La suite pasa completamente (23 tests).

---

## Cambio adicional — fix en permissions.py

**Justificación:** El AC "Test con destinatario None o vacío → debe incluir registro" requiere que `destinatario=None` no cause error y el registro sea incluido. La implementación original usaba `record.get('destinatario', '').lower()`, que falla con `AttributeError` cuando el valor presente es `None` (el default `''` solo aplica cuando la clave está ausente, no cuando el valor es `None`). El fix `(record.get('destinatario') or '').lower()` cubre ambos casos: clave ausente y valor `None`.

Mismo fix aplicado en `is_record_restricted` (línea 64) por simetría.

---

## Validación Kiro

**Fecha:** 2026-06-23

### Criterios de aceptación vs. Requirements

| Criterio tasks.md 5.3                             | Requirement validado                  | Estado      |
| ------------------------------------------------- | ------------------------------------- | ----------- |
| Test con usuario sin perfil definido → ValueError | 10.1 (must provide user identifier)   | ✅ Cumplido |
| Test con dataset vacío → lista vacía              | 5.6 (apply filter before RAG context) | ✅ Cumplido |
| Test con destinatario None o vacío → incluir      | 5.5 (case-insensitive matching)       | ✅ Cumplido |
| Test case-insensitive (MACRO, Macro, macro)       | 5.5 (case-insensitive matching)       | ✅ Cumplido |

### Hallazgos

1. **Bug fix crítico identificado y corregido**: El manejo de `destinatario=None` presentaba un bug (`AttributeError`). La corrección `(record.get('destinatario') or '').lower()` es **correcta** y **necesaria** para cumplir el AC "destinatario None o vacío → incluir registro". Sin este fix, los tests no pasarían.

2. **Cobertura completa de edge cases**: Los 9 unit tests cubren todas las situaciones no cubiertas por property tests:
   - Validación de entrada (user None, perfil vacío)
   - Dataset vacío
   - Destinatario ausente, None, o vacío
   - Case-insensitive matching exhaustivo (3 variantes)

3. **Sin regresiones**: Suite completa 23/23 OK.

4. **Documentación adecuada**: Cada test referencia el Requirement que valida.

### Veredicto

**COMPLETED** — La tarea 5.3 cumple todos sus criterios de aceptación, corrige un bug crítico encontrado durante testing (como debe ser), y mantiene la suite completa sin regresiones.
