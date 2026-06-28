# Devolución — home-chat-orchestrator-contract · Tarea 5.2

**Fecha:** 2026-06-26
**Spec:** home-chat-orchestrator-contract
**Tarea:** 5.2 — Escribir tests unitarios para serializers
**Veredicto Claude Code:** criterios cumplidos — pendiente validación Kiro
**Veredicto Kiro:** ✅ COMPLETED — todos los criterios cumplidos

---

## Qué se implementó

Se agregaron dos clases de test a `app/core/tests.py`, siguiendo el patrón establecido por las tareas 2.3, 3.2 y 4.2 (tests en archivo monolítico, no en archivos separados):

- `RequestPayloadSerializerTest` — 13 tests que cubren criterios 1–6
- `ResponsePayloadSerializerTest` — 6 tests que cubren criterios 7–8
- Total: 21 tests nuevos

También se agregaron las importaciones necesarias al bloque de imports de `tests.py`:

```python
from core.serializers.chat_serializers import (
    RequestPayloadSerializer,
    ResponsePayloadSerializer,
)
```

**Cambio adicional (bug fix durante implementación):**

- Línea extra `self.assertEqual(len(new_cid.split('-')), 3)` aparecía en `test_missing_agent_used_in_metadata_fails` por arrastre del contexto de edición. Removida antes de correr tests.
- `test_incorrect_type_memory_enabled_fails` usaba `'yes'` como valor inválido, pero DRF acepta `'yes'` como `True` (está en `BooleanField.TRUE_VALUES`). Corregido a `'maybe'`, que DRF rechaza correctamente.

---

## Criterios de aceptación — verificación punto a punto

| Criterio                                                       | Estado | Evidencia                                                                                                                                                                                                                                    |
| -------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RequestPayloadSerializer: payload válido pasa                  | ✅     | `test_valid_payload_passes` — `s.is_valid()` retorna `True`                                                                                                                                                                                  |
| RequestPayloadSerializer: campos requeridos faltantes fallan   | ✅     | `test_missing_query_fails`, `test_missing_user_fails`, `test_missing_conversation_id_fails`, `test_empty_query_fails` — `is_valid()` retorna `False` con el campo correcto en `s.errors`                                                     |
| RequestPayloadSerializer: tipos incorrectos fallan             | ✅     | `test_incorrect_type_user_id_fails` (`userId='not-an-int'`), `test_incorrect_type_memory_enabled_fails` (`memoryEnabled='maybe'`) — `is_valid()` retorna `False`                                                                             |
| RequestPayloadSerializer: conversationId inválido falla        | ✅     | `test_conversation_id_no_conv_prefix_fails` (prefijo incorrecto), `test_conversation_id_wrong_parts_fails` (2 partes), `test_conversation_id_too_many_parts_fails` (4 partes) — `is_valid()` retorna `False` con `conversationId` en errores |
| RequestPayloadSerializer: agentType inválido → fallback 'auto' | ✅     | `test_invalid_agent_type_falls_back_to_auto` — `agentType='unknown-agent'` → `s.validated_data['agentType'] == 'auto'`; también `test_valid_agent_type_rag_mails_passes` y `test_missing_agent_type_defaults_to_auto`                        |
| RequestPayloadSerializer: profile inválido falla               | ✅     | `test_invalid_profile_fails` (`profile='Desconocido'`) — `is_valid()` retorna `False`; `test_all_valid_profiles_pass` verifica los 5 perfiles válidos                                                                                        |
| ResponsePayloadSerializer: payload válido pasa                 | ✅     | `test_valid_response_passes`, `test_optional_error_field_passes`, `test_records_found_null_passes` — `is_valid()` retorna `True`                                                                                                             |
| ResponsePayloadSerializer: metadata faltante falla             | ✅     | `test_missing_metadata_fails`, `test_missing_output_fails`, `test_missing_agent_used_in_metadata_fails` — `is_valid()` retorna `False` con campo correcto en errores                                                                         |

---

## Resultado de tests

```
python3 -Wa manage.py test core.tests.RequestPayloadSerializerTest core.tests.ResponsePayloadSerializerTest
Ran 21 tests in 0.054s
OK
```

```
python3 -Wa manage.py test core
Ran 108 tests in 624.258s
OK
```

Suite completo: 108 tests, 0 failures, 0 errors.

---

## Archivos modificados

- `app/core/tests.py` — importaciones + clases `RequestPayloadSerializerTest` y `ResponsePayloadSerializerTest`

## Archivos NO modificados

- `app/core/serializers/chat_serializers.py` — sin cambios (ya estaba correcto)

---

## Validación Kiro — 2026-06-26

### Verificación contra requirements.md

La tarea 5.2 requiere tests unitarios que cubran TODAS las validaciones definidas en Requirement 3 (validación de Request_Payload) y estructuras definidas en Requirement 1 (Request_Payload) y Requirement 2 (Response_Payload).

**RequestPayloadSerializer:**

✅ Payload válido pasa → `test_valid_payload_passes` verifica `is_valid() == True`

✅ Campos requeridos faltantes → 4 tests específicos (`test_missing_query_fails`, `test_missing_user_fails`, `test_missing_conversation_id_fails`, `test_empty_query_fails`) verifican que `is_valid() == False` con campo correcto en errores

✅ Tipos incorrectos → 2 tests (`test_incorrect_type_user_id_fails`, `test_incorrect_type_memory_enabled_fails`) verifican rechazo de tipos inválidos

✅ conversationId inválido → 3 tests (`test_conversation_id_no_conv_prefix_fails`, `test_conversation_id_wrong_parts_fails`, `test_conversation_id_too_many_parts_fails`) verifican formato `conv-<timestamp>-<random>`

✅ agentType fallback → `test_invalid_agent_type_falls_back_to_auto` verifica que agentType inválido → 'auto', más 2 tests adicionales para casos válidos y default

✅ profile validación → `test_invalid_profile_fails` verifica rechazo de perfil inválido + `test_all_valid_profiles_pass` verifica los 5 perfiles válidos ("Administrador", "Usuario IC", "Heavy user", "Macro", "Usuario")

**ResponsePayloadSerializer:**

✅ Payload válido → 3 tests (`test_valid_response_passes`, `test_optional_error_field_passes`, `test_records_found_null_passes`) verifican estructuras válidas

✅ Metadata faltante → 3 tests (`test_missing_metadata_fails`, `test_missing_output_fails`, `test_missing_agent_used_in_metadata_fails`) verifican campos requeridos

### Evidencia ejecutable

```bash
$ python3 -Wa manage.py test core.tests.RequestPayloadSerializerTest core.tests.ResponsePayloadSerializerTest
Ran 21 tests in 0.062s
OK
```

```bash
$ python3 -Wa manage.py test core
Ran 108 tests in 678.362s
OK
```

### Hallazgos

1. **Bug fix durante implementación:** Correcto identificar y corregir `memoryEnabled='yes'` → `'maybe'` porque DRF acepta 'yes' como True en BooleanField
2. **Cobertura completa:** Los 21 tests cubren TODOS los criterios de tasks.md task 5.2
3. **0 failures, 0 errors:** Suite completo (108 tests) pasa sin errores
4. **Diseño correcto:** Tests siguen el patrón establecido (archivo monolítico tests.py, no archivos separados)

### Veredicto final

**✅ COMPLETED**

La tarea 5.2 cumple TODOS los criterios de aceptación:

- ✅ 8 criterios RequestPayloadSerializer cubiertos por 13 tests
- ✅ 2 criterios ResponsePayloadSerializer cubiertos por 8 tests
- ✅ 21 tests nuevos, todos pasan
- ✅ Suite completo 108 tests, 0 failures
- ✅ Implementación sigue patrones establecidos

**Próximo paso:** Marcar tarea 5.2 como [x] en tasks.md y proceder a tarea 6.1
