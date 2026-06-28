# Validación tarea 8.2 — Property tests load_demo_users

**Spec:** usuarios-demo-perfiles-permisos
**Tarea:** 8.2 — Write property test for load_demo_users validation
**Fecha:** 2026-06-23
**Veredicto Kiro:** ✅ **COMPLETED**

---

## Qué se implementó

Se agregó la clase `LoadDemoUsersPropertyTest(HypothesisTestCase)` en `app/core/tests.py` con tres property tests que validan la lógica de validación de `Command._validate()` del comando `load_demo_users`.

Se agregó también el import:

```python
from core.management.commands.load_demo_users import Command as LoadDemoUsersCommand
```

---

## Criterios de aceptación vs evidencia

| Criterio                                                                                                                                     | Estado        | Evidencia                                                                                                                                                                                                                             |
| -------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Property 7: Profile Validation** — Para cualquier perfil inválido, el comando debe rechazar con error                                      | ✅ cumplido   | `test_property_7_profile_validation` — hypothesis genera textos que no pertenecen a VALID_PROFILES, verifica que `_validate()` retorna errores con `'Perfil inválido'`. Test: OK                                                      |
| **Property 8: Invalid Role Assignment Rejection** — Para cualquier rol inválido asignado a Usuario IC, el comando debe rechazar con error    | ✅ cumplido   | `test_property_8_invalid_role_rejection` — hypothesis genera textos que no pertenecen a VALID_ROLES, verifica que `_validate()` retorna errores con `'Rol inválido'`. Test: OK                                                        |
| **Property 9: CSV Load Rejection on Missing Fields** — Para cualquier campo obligatorio faltante, el comando debe rechazar la carga completa | ✅ cumplido   | `test_property_9_csv_rejection_missing_fields` — hypothesis samplea entre `['first_name', 'last_name', 'email', 'perfil']`, vacía ese campo y verifica que `_validate()` retorna errores con `'campo obligatorio faltante'`. Test: OK |
| Validates Requirements 7.5, 8.3, 8.4                                                                                                         | ✅ confirmado | Property 9 → Req 7.5, Property 7 → Req 8.3, Property 8 → Req 8.4                                                                                                                                                                      |

---

## Resultado de ejecución

```
Ran 3 tests in 1.318s
OK
```

Suite completa (33 tests):

```
Ran 33 tests in 476.325s
OK
```

Sin regresiones.

---

## Archivos modificados

- `app/core/tests.py` — agregado import `LoadDemoUsersCommand` (línea 14) y clase `LoadDemoUsersPropertyTest` al final del archivo (~líneas 486–590)

---

## Validación Kiro

**Fecha validación:** 2026-06-23
**Validador:** Kiro

### Verificación contra requirements.md

**Requirement 7.5** (AC5 de Requirement 7):

> IF a user record in the CSV or fixture is missing required fields (nombre, apellido, email, perfil), THEN THE User_System SHALL reject the entire load operation

✅ **Validado**: Property 9 (`test_property_9_csv_rejection_missing_fields`) genera casos donde cualquier campo obligatorio está vacío y verifica que `_validate()` reporta error 'campo obligatorio faltante'. Hypothesis ejecutó 100 ejemplos sin contraejemplos.

**Requirement 8.3** (AC3 de Requirement 8):

> THE User_System SHALL validate that perfil is one of the 5 valid profiles

✅ **Validado**: Property 7 (`test_property_7_profile_validation`) genera textos arbitrarios que no pertenecen a los 5 perfiles válidos y verifica que `_validate()` reporta error 'Perfil inválido'. Hypothesis ejecutó 100 ejemplos sin contraejemplos.

**Requirement 8.4** (AC4 de Requirement 8):

> THE User_System SHALL validate that roles contains only valid role names when profile is Usuario IC

✅ **Validado**: Property 8 (`test_property_8_invalid_role_rejection`) genera textos arbitrarios que no pertenecen a los 7 roles válidos, los asigna a un Usuario IC, y verifica que `_validate()` reporta error 'Rol inválido'. Hypothesis ejecutó 100 ejemplos sin contraejemplos.

### Verificación contra tasks.md

**Tarea 8.2:**

> Write property test for load_demo_users validation
>
> - Property 7: Profile Validation
> - Property 8: Invalid Role Assignment Rejection
> - Property 9: CSV Load Rejection on Missing Fields
> - Validates: Requirements 7.5, 8.3, 8.4

✅ **Cumplido completamente**: Los tres property tests están implementados, ejecutan correctamente, y validan exactamente los tres requirements especificados.

### Verificación de regresiones

Suite completa ejecutada: **33 tests en 476.325s — OK**

✅ Sin regresiones detectadas.

### Calidad de implementación

**Puntos fuertes:**

- Los tests usan `hypothesis` correctamente con estrategias apropiadas (`st.emails()`, `st.text()`, `st.sampled_from()`)
- Los filtros aplicados a las estrategias son correctos (`.filter(lambda p: p.strip() not in ...)`)
- Las aserciones son precisas y verifican el mensaje de error específico esperado
- Los docstrings documentan claramente qué property valida cada test y qué requirement cubre
- Cobertura completa: 100 ejemplos por property (default de hypothesis)

**Observaciones menores:**

- En Property 8, línea 530, se agrega `or '\x00'` como fallback para garantizar que el rol no sea vacío post-strip. Esto es defensivo pero innecesario dado el filtro en la estrategia; sin embargo, no afecta la corrección del test.

### Decisión final

**Veredicto:** ✅ **COMPLETED**

La tarea 8.2 cumple completamente con sus criterios de aceptación:

- Las tres properties están implementadas correctamente
- Los requirements 7.5, 8.3 y 8.4 están validados
- La suite completa ejecuta sin errores ni regresiones
- La implementación sigue las convenciones de hypothesis y el estándar del proyecto

**Siguiente paso:** Marcar tarea 8.2 como [x] en tasks.md y actualizar PROGRESO.md.
