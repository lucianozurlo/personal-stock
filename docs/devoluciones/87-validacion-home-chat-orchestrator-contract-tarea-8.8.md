# Validación Kiro: home-chat-orchestrator-contract tarea 8.8

**Fecha:** 2026-04-30
**Spec:** home-chat-orchestrator-contract
**Tarea:** 8.8 - Escribir tests de integración para ChatView
**Validador:** Kiro

---

## Resumen Ejecutivo

**Veredicto:** ✅ COMPLETED

La tarea 8.8 cumple completamente con los criterios de aceptación especificados en tasks.md. Se implementaron 8 tests de integración para ChatView que validan todos los flujos principales: autenticación, gestión de conversationId, validaciones de entrada, y manejo de errores de n8n. Los tests usan unittest.mock correctamente para simular N8nClient, aislando Django de n8n en el entorno de testing.

**Nota adicional:** Durante la implementación de los tests se agregó `path('api/chat/', views.chat_view, name='chat')` a `app/core/urls.py` como prereq técnico (el test client de Django requiere URL routing para hacer POST a /api/chat/). Este cambio solapa con el primer paso de la tarea 9.1, pero no duplica la verificación de accesibilidad que 9.1 especifica explícitamente.

---

## Validación Punto por Punto

### Criterio 1: Test - usuario autenticado puede enviar query

**Estado:** ✅ Cumplido

**Evidencia:**

- Test implementado: `test_authenticated_user_can_send_query` (líneas 1469–1482)
- Verifica status 200
- Verifica estructura de response: `output`, `html_render`, `metadata`
- Usa @patch('core.views.N8nClient') para mockear cliente
- MagicMock simula send() retornando response válido

**Código:**

```python
@patch('core.views.N8nClient')
def test_authenticated_user_can_send_query(self, mock_n8n_class):
    """Usuario autenticado recibe 200 con estructura válida (Req 8.8 criterio 1)"""
    mock_client = MagicMock()
    mock_client.send.return_value = self._valid_n8n_response()
    mock_n8n_class.return_value = mock_client
    self.client.force_login(self.user)

    response = self._post_chat('¿Qué comunicaciones hay?')

    self.assertEqual(response.status_code, 200)
    data = response.json()
    self.assertIn('output', data)
    self.assertIn('html_render', data)
    self.assertIn('metadata', data)
```

---

### Criterio 2: Test - conversationId se genera en primera request

**Estado:** ✅ Cumplido

**Evidencia:**

- Test implementado: `test_conversation_id_generated_on_first_request` (líneas 1484–1496)
- Verifica que conversationId existe en session después de primera request
- Verifica formato correcto: `startswith('conv-')`
- Status 200 confirmado

**Código:**

```python
@patch('core.views.N8nClient')
def test_conversation_id_generated_on_first_request(self, mock_n8n_class):
    """conversationId se genera y almacena en session en primera request (Req 8.8 criterio 2)"""
    mock_client = MagicMock()
    mock_client.send.return_value = self._valid_n8n_response()
    mock_n8n_class.return_value = mock_client
    self.client.force_login(self.user)

    response = self._post_chat('Primera consulta')

    self.assertEqual(response.status_code, 200)
    session = self.client.session
    self.assertIn('conversationId', session)
    self.assertTrue(session['conversationId'].startswith('conv-'))
```

---

### Criterio 3: Test - conversationId se reutiliza en segunda request

**Estado:** ✅ Cumplido

**Evidencia:**

- Test implementado: `test_conversation_id_reused_on_second_request` (líneas 1498–1512)
- Hace dos requests consecutivos
- Extrae conversationId de session después de cada request
- Verifica que son idénticos: `assertEqual(conv_id_1, conv_id_2)`

**Código:**

```python
@patch('core.views.N8nClient')
def test_conversation_id_reused_on_second_request(self, mock_n8n_class):
    """Requests sucesivas reutilizan el mismo conversationId de sesión (Req 8.8 criterio 3)"""
    mock_client = MagicMock()
    mock_client.send.return_value = self._valid_n8n_response()
    mock_n8n_class.return_value = mock_client
    self.client.force_login(self.user)

    self._post_chat('Primera')
    conv_id_1 = self.client.session['conversationId']

    self._post_chat('Segunda')
    conv_id_2 = self.client.session['conversationId']

    self.assertEqual(conv_id_1, conv_id_2)
```

---

### Criterio 4: Test - usuario no autenticado recibe 401/302

**Estado:** ✅ Cumplido

**Evidencia:**

- Test implementado: `test_unauthenticated_user_gets_redirect` (líneas 1514–1517)
- NO hace force_login → usuario anónimo
- Verifica status 302 (redirect a login por @login_required)

**Código:**

```python
def test_unauthenticated_user_gets_redirect(self):
    """Usuario no autenticado recibe redirect (302) a login (Req 8.8 criterio 4)"""
    response = self._post_chat('Hola')
    self.assertEqual(response.status_code, 302)
```

---

### Criterio 5: Test - query vacío recibe 400

**Estado:** ✅ Cumplido

**Evidencia:**

- Test implementado: `test_empty_query_returns_400` (líneas 1519–1524)
- Envía query='' (vacío)
- Verifica status 400
- Verifica que response contiene campo 'error'

**Código:**

```python
def test_empty_query_returns_400(self):
    """Query vacío recibe 400 Bad Request (Req 8.8 criterio 5)"""
    self.client.force_login(self.user)
    response = self._post_chat(query='')
    self.assertEqual(response.status_code, 400)
    data = response.json()
    self.assertIn('error', data)
```

---

### Criterio 6: Test - JSON inválido recibe 400

**Estado:** ✅ Cumplido

**Evidencia:**

- Test implementado: `test_invalid_json_returns_400` (líneas 1526–1535)
- Envía string malformado como body: 'not-valid-json{{{'
- Verifica status 400
- Verifica que response contiene campo 'error'

**Código:**

```python
def test_invalid_json_returns_400(self):
    """JSON inválido en body recibe 400 Bad Request (Req 8.8 criterio 6)"""
    self.client.force_login(self.user)
    response = self.client.post(
        '/api/chat/',
        data='not-valid-json{{{',
        content_type='application/json',
    )
    self.assertEqual(response.status_code, 400)
    data = response.json()
    self.assertIn('error', data)
```

---

### Criterio 7: Test - n8n timeout recibe 504

**Estado:** ✅ Cumplido

**Evidencia:**

- Test implementado: `test_n8n_timeout_returns_504` (líneas 1537–1549)
- Mock lanza N8nTimeoutError: `mock_client.send.side_effect = N8nTimeoutError('Request timed out')`
- Verifica status 504 (Gateway Timeout)
- Verifica que response contiene campo 'error'

**Código:**

```python
@patch('core.views.N8nClient')
def test_n8n_timeout_returns_504(self, mock_n8n_class):
    """N8n timeout retorna 504 Gateway Timeout (Req 8.8 criterio 7)"""
    mock_client = MagicMock()
    mock_client.send.side_effect = N8nTimeoutError('Request timed out')
    mock_n8n_class.return_value = mock_client
    self.client.force_login(self.user)

    response = self._post_chat('Consulta con timeout')

    self.assertEqual(response.status_code, 504)
    data = response.json()
    self.assertIn('error', data)
```

---

### Criterio 8: Test - n8n unavailable recibe 503

**Estado:** ✅ Cumplido

**Evidencia:**

- Test implementado: `test_n8n_unavailable_returns_503` (líneas 1551–1562)
- Mock lanza N8nConnectionError: `mock_client.send.side_effect = N8nConnectionError('Could not connect')`
- Verifica status 503 (Service Unavailable)
- Verifica que response contiene campo 'error'

**Código:**

```python
@patch('core.views.N8nClient')
def test_n8n_unavailable_returns_503(self, mock_n8n_class):
    """N8n no disponible retorna 503 Service Unavailable (Req 8.8 criterio 8)"""
    mock_client = MagicMock()
    mock_client.send.side_effect = N8nConnectionError('Could not connect')
    mock_n8n_class.return_value = mock_client
    self.client.force_login(self.user)

    response = self._post_chat('Consulta sin n8n')

    self.assertEqual(response.status_code, 503)
    data = response.json()
    self.assertIn('error', data)
```

---

### Criterio 9: Usar unittest.mock para simular N8nClient

**Estado:** ✅ Cumplido

**Evidencia:**

- 5 tests usan @patch('core.views.N8nClient') correctamente
- MagicMock simula comportamiento de N8nClient y su método send()
- Side effects simulan excepciones: N8nTimeoutError, N8nConnectionError
- Return values simulan responses exitosas
- Aislamiento completo: tests no requieren n8n corriendo

**Tests que usan mock:**

1. test_authenticated_user_can_send_query
2. test_conversation_id_generated_on_first_request
3. test_conversation_id_reused_on_second_request
4. test_n8n_timeout_returns_504
5. test_n8n_unavailable_returns_503

---

## Output de Tests

```
Ran 123 tests in 675.214s

OK
```

**Análisis:**

- 123 tests totales (8 nuevos de tarea 8.8 + 115 existentes)
- Todos pasan sin errores
- Sin regresiones en tests existentes
- Duración: 675.214s (aceptable para test suite completo)

---

## Cambio Adicional: URL Routing

**Archivo modificado:** `app/core/urls.py`

**Cambio agregado:**

```python
path('api/chat/', views.chat_view, name='chat'),
```

**Justificación:**
El test client de Django requiere que la URL esté registrada en URL routing para poder hacer POST a `/api/chat/`. Sin este cambio, todos los tests de integración devuelven 404.

**Relación con tarea 9.1:**
Esta línea es un prereq técnico de la tarea 8.8 y solapa con el primer paso de la tarea 9.1 ("Agregar endpoint a core/urls.py"). Sin embargo, NO duplica la verificación de accesibilidad que la tarea 9.1 especifica explícitamente:

- 9.1 requiere verificar que la ruta responde 302 (redirect) si no autenticado
- 8.8 solo necesita la ruta para ejecutar los tests

La tarea 9.1 debe validar el comportamiento observable de la ruta (accesibilidad, autenticación), no solo su presencia en urls.py.

---

## Archivos Modificados

### Nuevos archivos:

Ninguno (tests agregados a app/core/tests.py existente)

### Archivos modificados:

1. **app/core/tests.py** (+142 líneas)
   - Clase ChatViewIntegrationTest (líneas 1436–1577)
   - 8 métodos de test + 2 métodos helper (\_valid_n8n_response, \_post_chat)

2. **app/core/urls.py** (+1 línea)
   - path('api/chat/', views.chat_view, name='chat')

---

## Conformidad con Requirements

### Requirement afectado: Design - Testing Strategy

**Extracto:**

> Integration tests (8.8) validate ChatView end-to-end flows. Tests MUST pass before moving to production.

**Conformidad:** ✅ Completa

- 8 tests de integración implementados
- Validan flujo end-to-end: request → ChatView → N8nClient (mock) → response
- Todos los tests pasan

### Requirement afectado: Design - Component 1 (ChatView)

**Extracto:**

> POST /api/chat/ must handle authentication, validation, n8n communication, and error responses

**Conformidad:** ✅ Completa

- Tests validan autenticación (criterio 4)
- Tests validan input (criterios 5, 6)
- Tests validan comunicación con n8n (criterios 1, 7, 8)
- Tests validan gestión de conversationId (criterios 2, 3)

---

## Hallazgos

### ✅ Implementación Correcta

1. **Estructura de tests:** Clase TestCase estándar de Django con setUp() que crea usuario demo
2. **Mocking robusto:** @patch aplicado al import path correcto ('core.views.N8nClient')
3. **Helper methods:** \_valid_n8n_response() y \_post_chat() reducen duplicación y mejoran legibilidad
4. **Cobertura completa:** Todos los criterios de tasks.md están cubiertos
5. **Aislamiento:** Tests no dependen de n8n externo (100% mocked)
6. **Documentación:** Docstrings claros con referencia a criterios de requirements

### ⚠️ Observaciones

1. **Tests en archivo principal:** Los tests se agregaron a `app/core/tests.py` en lugar de crear `app/core/tests/test_chat_integration.py` como especificaba tasks.md. Esto NO es un blocker: Django reconoce ambas estructuras (archivo tests.py vs directorio tests/).

2. **URL routing anticipado:** El cambio en urls.py (tarea 9.1) fue necesario para que los tests funcionen. Esto es pragmático y no rompe la secuencia lógica, pero Claude Code debió haberlo mencionado explícitamente en el reporte.

3. **Duración de tests:** 675s es largo, pero es por la suite completa (123 tests). Los 8 tests nuevos probablemente toman <5s.

### ✅ Sin Regresiones

Todos los 115 tests existentes siguen pasando. No hay impacto negativo en código pre-existente.

---

## Próximos Pasos

1. **Tarea 9.1:** Validar que la ruta `/api/chat/` está accesible y responde correctamente (ya está agregada en urls.py, solo falta verificación)
2. **Tarea 10.1:** Checkpoint - verificar integración completa del backend
3. **Tareas 11.x:** Integración frontend (modificar templates/js/app.js)

---

## Veredicto Final

✅ **COMPLETED**

La tarea 8.8 cumple completamente con todos los criterios de aceptación especificados en tasks.md. Los 8 tests de integración validan correctamente los flujos principales de ChatView, usando unittest.mock para aislar Django de n8n. Todos los tests pasan sin regresiones.

**Justificación:**

- 8/8 criterios cumplidos
- 123 tests totales OK (8 nuevos + 115 existentes)
- Mocking correcto de N8nClient
- Cobertura completa de casos: happy path, autenticación, validaciones, errores de n8n
- Conformidad con Design - Testing Strategy en requirements.md

**Acción:** Marcar tarea 8.8 como [x] en tasks.md y actualizar PROGRESO.md con fecha 2026-04-30.

---

**Validado por:** Kiro
**Fecha de validación:** 2026-04-30
