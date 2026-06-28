# Devolución: home-chat-orchestrator-contract — Tarea 6.2

**Fecha:** 2026-06-26
**Spec:** home-chat-orchestrator-contract
**Tarea:** 6.2 — Escribir tests unitarios para N8nClient
**Archivo modificado:** `app/core/tests.py` (clase `N8nClientTest` agregada al final)
**Veredicto:** ✅ COMPLETED

---

## Qué se validó

La tarea 6.2 requiere implementar 7 tests unitarios para `N8nClient` que validen:

1. Request exitoso retorna response_data
2. Timeout lanza N8nTimeoutError
3. Connection error lanza N8nConnectionError
4. Status != 200 lanza N8nConnectionError
5. Body vacío lanza N8nInvalidResponseError
6. JSON inválido lanza N8nInvalidResponseError
7. N8N_WEBHOOK_URL no configurada lanza ValueError

Todos los tests deben usar `unittest.mock` para simular `requests.post` sin hacer llamadas HTTP reales.

---

## Hallazgos

### ✅ Implementación correcta

**Clase N8nClientTest agregada** (`app/core/tests.py`, líneas 1347-1435):

- 7 tests unitarios implementados
- Imports correctos: `unittest.mock` (patch, MagicMock), `requests`, excepciones de `N8nClient`
- Primera vez que el proyecto usa mocking para HTTP (patrón correcto establecido)

**Test 1: test_successful_request_returns_response_data**

- Mock POST retorna status 200 + JSON válido `{"output": "ok", "html_render": true}`
- Verifica que `client.send(payload)` retorna el dict esperado
- Verifica con `assert_called_once_with()` que se llama con URL, json, headers, timeout=30
- ✅ Cumple criterio 1

**Test 2: test_timeout_raises_N8nTimeoutError**

- Mock `side_effect = requests_lib.Timeout()`
- Verifica que `assertRaises(N8nTimeoutError)` se lanza
- ✅ Cumple criterio 2

**Test 3: test_connection_error_raises_N8nConnectionError**

- Mock `side_effect = requests_lib.ConnectionError()`
- Verifica que `assertRaises(N8nConnectionError)` se lanza
- ✅ Cumple criterio 3

**Test 4: test_non_200_status_raises_N8nConnectionError**

- Mock status_code = 500
- Verifica que `assertRaises(N8nConnectionError)` se lanza
- ✅ Cumple criterio 4

**Test 5: test_empty_body_raises_N8nInvalidResponseError**

- Mock `content = b''` (body vacío)
- Verifica que `assertRaises(N8nInvalidResponseError)` se lanza
- ✅ Cumple criterio 5

**Test 6: test_invalid_json_raises_N8nInvalidResponseError**

- Mock `json.side_effect = ValueError("No JSON object could be decoded")`
- Verifica que `assertRaises(N8nInvalidResponseError)` se lanza
- ✅ Cumple criterio 6

**Test 7: test_missing_webhook_url_raises_ValueError**

- Usa `patch.dict(os.environ, {}, clear=False)` + `os.environ.pop('N8N_WEBHOOK_URL', None)`
- Verifica que `N8nClient()` (sin args) lanza `ValueError`
- ✅ Cumple criterio 7

### ✅ Ejecución exitosa

```
python3 -Wa manage.py test core.tests.N8nClientTest -v 2

Ran 7 tests in 0.007s
OK
```

Todos los tests pasan sin errores.

### ✅ Validación contra requirements.md

- **Requirement 5 (HTTP POST a n8n)**: Tests validan timeout, headers, payload
- **Requirement 7 (Manejo de errores)**: Tests cubren timeout, connection error, status != 200, body vacío, JSON inválido
- **Design - Testing Strategy**: Tests unitarios con mocking (patrón correcto)
- **Design - Component 5 (N8nClient)**: Todas las excepciones están testeadas

---

## Criterios de aceptación (tasks.md tarea 6.2)

| Criterio                                              | Estado      | Evidencia                                                                                                                                                       |
| ----------------------------------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Test: request exitoso retorna response_data           | ✅ Cumplido | `test_successful_request_returns_response_data` — mock POST 200 + JSON válido → assertEqual + assert_called_once_with (verifica URL, json, headers, timeout=30) |
| Test: timeout lanza N8nTimeoutError                   | ✅ Cumplido | `test_timeout_raises_N8nTimeoutError` — mock side_effect = requests.Timeout() → assertRaises(N8nTimeoutError)                                                   |
| Test: connection error lanza N8nConnectionError       | ✅ Cumplido | `test_connection_error_raises_N8nConnectionError` — mock side_effect = requests.ConnectionError() → assertRaises(N8nConnectionError)                            |
| Test: status != 200 lanza N8nConnectionError          | ✅ Cumplido | `test_non_200_status_raises_N8nConnectionError` — mock status 500 → assertRaises(N8nConnectionError)                                                            |
| Test: body vacío lanza N8nInvalidResponseError        | ✅ Cumplido | `test_empty_body_raises_N8nInvalidResponseError` — content = b'' → assertRaises(N8nInvalidResponseError)                                                        |
| Test: JSON inválido lanza N8nInvalidResponseError     | ✅ Cumplido | `test_invalid_json_raises_N8nInvalidResponseError` — json.side_effect = ValueError → assertRaises(N8nInvalidResponseError)                                      |
| Test: N8N_WEBHOOK_URL no configurada lanza ValueError | ✅ Cumplido | `test_missing_webhook_url_raises_ValueError` — patch.dict + pop('N8N_WEBHOOK_URL') + N8nClient() sin args → assertRaises(ValueError)                            |
| Usar unittest.mock para simular requests.post         | ✅ Cumplido | @patch('core.clients.n8n_client.requests.post') + MagicMock() en 6 de 7 tests; test 7 sin HTTP call                                                             |

---

## Archivos modificados

- `app/core/tests.py`: Agregada clase `N8nClientTest` (≈85 líneas) + imports de `unittest.mock`, `requests`, `core.clients.n8n_client`

---

## Veredicto final

**✅ COMPLETED**

La tarea 6.2 cumple todos los criterios de aceptación:

- 7 tests unitarios implementados correctamente
- Uso correcto de `unittest.mock` para simular HTTP (patrón establecido para el proyecto)
- Todos los tests pasan sin errores
- Cobertura completa de casos de éxito y error del `N8nClient`
- Validación contra requirements.md confirmada

**Próximos pasos:**

- Marcar tarea 6.2 como `[x]` en tasks.md ✅ (ya realizado)
- Actualizar PROGRESO.md con gate 6.2 pasado ✅ (ya realizado)
- Proceder a tarea 7.1: "Verificar que todos los helpers, serializers y client están implementados"
