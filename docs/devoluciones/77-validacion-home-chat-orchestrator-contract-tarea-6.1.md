# Validación Kiro: home-chat-orchestrator-contract tarea 6.1

**Fecha:** 2026-06-26
**Spec:** home-chat-orchestrator-contract
**Tarea:** 6.1 — Implementar cliente HTTP para n8n
**Validador:** Kiro

---

## Resumen ejecutivo

La tarea 6.1 (Implementar cliente HTTP para n8n) ha sido **completada exitosamente**. Claude Code reportó evidencia completa de cumplimiento contra todos los criterios de aceptación definidos en `tasks.md`. La implementación cumple con:

- ✅ Estructura de excepciones jerárquica correcta (base + 3 específicas)
- ✅ Inicialización con variable de entorno `N8N_WEBHOOK_URL`
- ✅ Método `send()` con timeout de 30 segundos
- ✅ Manejo completo de errores (5 casos: status != 200, body vacío, JSON inválido, timeout, connection error)
- ✅ Suite de tests sin regresiones (108 tests pasan)

La implementación sigue el diseño especificado en `design.md` Component 5 y cumple con requirements Requirement 5 (envío de payload) y Requirement 7 (manejo de errores).

**Veredicto:** COMPLETED

---

## Validación contra criterios de aceptación

### Criterio 1: Crear archivo app/core/clients/n8n_client.py

**Estado:** ✅ CUMPLIDO

**Evidencia:**

- Archivo creado en la ruta especificada
- Importable desde otros módulos del proyecto
- Estructura de código válida en Python

**Líneas relevantes:** Archivo completo (70 líneas)

---

### Criterio 2: Definir excepción N8nClientError (base)

**Estado:** ✅ CUMPLIDO

**Evidencia:**

```python
class N8nClientError(Exception):
    pass
```

**Ubicación:** Línea 11

**Validación:**

- Hereda de `Exception` (base de todas las excepciones Python)
- Actúa como excepción base para todas las excepciones específicas del cliente n8n
- Permite catch genérico con `except N8nClientError` para capturar todos los errores del cliente

---

### Criterio 3: Definir excepción N8nConnectionError

**Estado:** ✅ CUMPLIDO

**Evidencia:**

```python
class N8nConnectionError(N8nClientError):
    pass
```

**Ubicación:** Línea 15

**Validación:**

- Hereda de `N8nClientError` (jerarquía correcta)
- Se usa cuando la conexión HTTP falla o el servidor responde con status != 200
- Permite distinguir errores de conexión de otros tipos de errores

---

### Criterio 4: Definir excepción N8nTimeoutError

**Estado:** ✅ CUMPLIDO

**Evidencia:**

```python
class N8nTimeoutError(N8nClientError):
    pass
```

**Ubicación:** Línea 19

**Validación:**

- Hereda de `N8nClientError` (jerarquía correcta)
- Se usa cuando `requests.Timeout` es capturado
- Permite manejar timeouts específicamente (caso importante para sistemas distribuidos)

---

### Criterio 5: Definir excepción N8nInvalidResponseError

**Estado:** ✅ CUMPLIDO

**Evidencia:**

```python
class N8nInvalidResponseError(N8nClientError):
    pass
```

**Ubicación:** Línea 23

**Validación:**

- Hereda de `N8nClientError` (jerarquía correcta)
- Se usa cuando el body está vacío o el JSON es inválido
- Permite distinguir errores de parseo de errores de red

---

### Criterio 6: **init** obtiene URL de os.environ.get('N8N_WEBHOOK_URL')

**Estado:** ✅ CUMPLIDO

**Evidencia:**

```python
def __init__(self, webhook_url: Optional[str] = None):
    self.webhook_url = webhook_url or os.environ.get('N8N_WEBHOOK_URL')
    if not self.webhook_url:
        raise ValueError('N8N_WEBHOOK_URL not configured')
```

**Ubicación:** Línea 30

**Validación:**

- Acepta `webhook_url` opcional como parámetro (útil para tests)
- Fallback a variable de entorno `N8N_WEBHOOK_URL` si no se provee
- Usa `os.environ.get()` (no `os.environ[]` que lanza KeyError si falta)
- Almacena URL en `self.webhook_url` para uso posterior

---

### Criterio 7: **init** lanza ValueError si no hay URL configurada

**Estado:** ✅ CUMPLIDO

**Evidencia:**

```python
if not self.webhook_url:
    raise ValueError('N8N_WEBHOOK_URL not configured')
```

**Ubicación:** Líneas 31-32

**Validación:**

- Verifica que `webhook_url` no sea None, cadena vacía, u otro valor falsy
- Lanza `ValueError` (tipo estándar Python para argumentos inválidos)
- Mensaje descriptivo que indica el problema exacto
- Claude Code verificó manualmente: "ValueError OK: N8N_WEBHOOK_URL not configured"

---

### Criterio 8: send() con timeout de 30 segundos

**Estado:** ✅ CUMPLIDO

**Evidencia:**

```python
TIMEOUT = 30  # línea 27

response = requests.post(
    self.webhook_url,
    json=payload,
    headers={'Content-Type': 'application/json'},
    timeout=self.TIMEOUT,  # línea 41
)
```

**Ubicación:** Líneas 27 (constante), 41 (uso)

**Validación:**

- Constante de clase `TIMEOUT = 30` define el valor
- Se pasa `timeout=self.TIMEOUT` a `requests.post()`
- 30 segundos es el valor especificado en Requirement 7 AC6
- Previene espera indefinida cuando n8n no responde

---

### Criterio 9: status != 200 → N8nConnectionError

**Estado:** ✅ CUMPLIDO

**Evidencia:**

```python
if response.status_code != 200:
    raise N8nConnectionError(
        f"n8n returned HTTP {response.status_code}: {response.text}"
    )
```

**Ubicación:** Líneas 43-46

**Validación:**

- Verifica `response.status_code != 200` (no acepta 201, 204, etc.)
- Lanza `N8nConnectionError` específica
- Mensaje incluye status code y texto de respuesta para debugging
- Rechaza errores 4xx y 5xx del servidor n8n

---

### Criterio 10: body vacío → N8nInvalidResponseError

**Estado:** ✅ CUMPLIDO

**Evidencia:**

```python
if not response.content:
    raise N8nInvalidResponseError(
        "n8n responded 200 but with empty body"
    )
```

**Ubicación:** Líneas 48-51

**Validación:**

- Verifica `not response.content` (body vacío o None)
- Lanza `N8nInvalidResponseError` específica
- Mensaje descriptivo que indica status 200 pero body vacío
- Alineado con Requirement 6 AC2 (error si body vacío)

---

### Criterio 11: JSON inválido → N8nInvalidResponseError

**Estado:** ✅ CUMPLIDO

**Evidencia:**

```python
try:
    return response.json()
except ValueError as e:
    raise N8nInvalidResponseError(
        f"Response is not valid JSON: {response.text[:200]}"
    ) from e
```

**Ubicación:** Líneas 53-58

**Validación:**

- Intenta parsear JSON con `response.json()`
- Captura `ValueError` (lanzado por `json.loads()` cuando JSON inválido)
- Re-lanza como `N8nInvalidResponseError` específica
- Mensaje incluye primeros 200 caracteres del body para debugging
- Usa `from e` para preservar stack trace original (best practice Python)

---

### Criterio 12: requests.Timeout → N8nTimeoutError

**Estado:** ✅ CUMPLIDO

**Evidencia:**

```python
except requests.Timeout as e:
    raise N8nTimeoutError(
        f"Request to n8n timed out after {self.TIMEOUT}s"
    ) from e
```

**Ubicación:** Líneas 60-63

**Validación:**

- Captura `requests.Timeout` específicamente
- Re-lanza como `N8nTimeoutError` específica
- Mensaje incluye el timeout configurado (30s)
- Usa `from e` para preservar stack trace
- Alineado con Requirement 7 AC2 (manejar timeout)

---

### Criterio 13: requests.ConnectionError → N8nConnectionError

**Estado:** ✅ CUMPLIDO

**Evidencia:**

```python
except requests.ConnectionError as e:
    raise N8nConnectionError(
        f"Could not connect to n8n at {self.webhook_url}"
    ) from e
```

**Ubicación:** Líneas 64-67

**Validación:**

- Captura `requests.ConnectionError` específicamente (red no disponible, host no resuelve DNS, etc.)
- Re-lanza como `N8nConnectionError` específica
- Mensaje incluye la URL que intentó conectar
- Usa `from e` para preservar stack trace
- Alineado con Requirement 7 AC2 (manejar connection error)

---

### Criterio 14: Suite de tests sin regresiones

**Estado:** ✅ CUMPLIDO

**Evidencia:**

```
Ran 108 tests in 525.263s

OK
```

**Validación:**

- Todos los tests del proyecto pasan sin errores
- No se introdujeron regresiones al agregar el nuevo módulo
- 108 tests es la cantidad esperada (suite completa anterior sin tests unitarios para N8nClient aún)
- La tarea 6.2 agregará tests unitarios específicos para N8nClient

**Nota:** Los tests unitarios para `N8nClient` se implementan en la tarea 6.2 (siguiente tarea). Esta tarea 6.1 solo verifica que el código nuevo no rompe los tests existentes.

---

## Validación contra requirements.md

### Requirement 5: Enviar Request_Payload al webhook de n8n

**AC1:** THE Django_Frontend SHALL send Request_Payload to the URL defined in environment variable `N8N_WEBHOOK_URL` using HTTP POST method

**Cumplimiento:** ✅ CUMPLIDO

- `os.environ.get('N8N_WEBHOOK_URL')` obtiene la URL
- `requests.post()` envía con método HTTP POST

**AC2:** THE Django_Frontend SHALL set HTTP header `Content-Type: application/json` when sending Request_Payload

**Cumplimiento:** ✅ CUMPLIDO

```python
headers={'Content-Type': 'application/json'}
```

**AC3:** THE Django_Frontend SHALL serialize Request_Payload as valid JSON before sending

**Cumplimiento:** ✅ CUMPLIDO

```python
json=payload  # requests serializa automáticamente a JSON
```

---

### Requirement 7: Manejar errores de comunicación con N8n_Orchestrator

**AC1:** IF the N8n_Orchestrator returns HTTP status code other than 200, THEN THE Django_Frontend SHALL display error message "Error conectando con n8n: HTTP <status_code> - <response_body>"

**Cumplimiento:** ✅ CUMPLIDO

- Lanza `N8nConnectionError` con mensaje `f"n8n returned HTTP {response.status_code}: {response.text}"`
- La vista (tarea 8) convertirá esta excepción en el mensaje user-facing

**AC2:** IF the network request to N8n_Orchestrator fails due to connection error or timeout, THEN THE Django_Frontend SHALL display error message "Error conectando con n8n: <error_description>"

**Cumplimiento:** ✅ CUMPLIDO

- Timeout → `N8nTimeoutError` con descripción
- Connection error → `N8nConnectionError` con descripción
- La vista (tarea 8) convertirá estas excepciones en mensajes user-facing

**AC6:** THE Django_Frontend SHALL set a timeout of 30 seconds for requests to N8n_Orchestrator to prevent indefinite waiting

**Cumplimiento:** ✅ CUMPLIDO

- `TIMEOUT = 30` y `timeout=self.TIMEOUT` en requests.post()

---

## Validación contra design.md

### Component 5: N8nClient

**Interface definida:**

- ✅ Excepciones: `N8nClientError`, `N8nConnectionError`, `N8nTimeoutError`, `N8nInvalidResponseError`
- ✅ `__init__(webhook_url: Optional[str] = None)`: constructor con URL opcional
- ✅ `send(payload: Dict[str, Any]) -> Dict[str, Any]`: método principal
- ✅ `TIMEOUT = 30`: constante de timeout

**Responsibilities cumplidas:**

- ✅ Send Request_Payload to n8n webhook
- ✅ Handle HTTP connection, timeout (30s)
- ✅ Parse Response_Payload from n8n
- ✅ Handle errors (connection, timeout, invalid response)
- ✅ Return errors to ChatView for handling

**Error Handling Flow:**

- ✅ Status != 200 → `N8nConnectionError`
- ✅ Empty body → `N8nInvalidResponseError`
- ✅ Invalid JSON → `N8nInvalidResponseError`
- ✅ Timeout → `N8nTimeoutError`
- ✅ Connection error → `N8nConnectionError`

---

## Hallazgos

### Fortalezas

1. **Jerarquía de excepciones clara y correcta**
   - Base `N8nClientError` permite catch genérico
   - Excepciones específicas permiten manejo granular
   - Herencia correcta en todas las excepciones

2. **Manejo robusto de errores**
   - Cubre todos los casos especificados en requirements
   - Mensajes descriptivos con contexto (URL, status, timeout duration)
   - Usa `from e` para preservar stack traces (best practice Python)

3. **Interface limpia y simple**
   - `send(payload)` es el único método público
   - Constructor flexible (acepta URL o usa env var)
   - Validación temprana (ValueError si no hay URL configurada)

4. **Configuración por variable de entorno**
   - Sigue best practices (12-factor app)
   - `N8N_WEBHOOK_URL` ya existe en `.env.example`
   - Permite override por parámetro (útil para tests)

5. **Alineación con diseño**
   - Implementación coincide 100% con `design.md` Component 5
   - Todos los campos y métodos especificados están presentes
   - Orden de manejo de errores correcto (status → body vacío → JSON inválido → timeout → connection)

### Sin issues detectados

No se detectaron problemas, gaps ni desviaciones del spec.

---

## Próximos pasos

1. **Tarea 6.2 (siguiente):** Escribir tests unitarios para N8nClient
   - Test request exitoso retorna response_data
   - Test timeout lanza `N8nTimeoutError`
   - Test connection error lanza `N8nConnectionError`
   - Test status != 200 lanza `N8nConnectionError`
   - Test body vacío lanza `N8nInvalidResponseError`
   - Test JSON inválido lanza `N8nInvalidResponseError`
   - Test `N8N_WEBHOOK_URL` no configurada lanza `ValueError`
   - Usar `unittest.mock` para simular `requests.post`

2. **Tarea 7.1:** Checkpoint - Verificar que todos los componentes individuales están completos

3. **Tarea 8.x:** Implementar ChatView que integrará N8nClient

---

## Veredicto final

**Estado:** ✅ COMPLETED

**Justificación:**

Todos los criterios de aceptación de la tarea 6.1 están cumplidos:

- ✅ Archivo creado
- ✅ 4 excepciones definidas correctamente
- ✅ `__init__` obtiene URL de variable de entorno
- ✅ `__init__` lanza ValueError si no hay URL
- ✅ `send()` con timeout de 30 segundos
- ✅ 5 casos de error manejados correctamente
- ✅ Suite de tests sin regresiones

La implementación es consistente con:

- requirements.md Requirement 5, Requirement 7
- design.md Component 5
- tasks.md tarea 6.1

**Acción:** Marcar tarea 6.1 como `[x]` en tasks.md y actualizar PROGRESO.md con próxima tarea 6.2.

---

**Validado por:** Kiro
**Fecha:** 2026-06-26
**Spec:** home-chat-orchestrator-contract
**Tarea:** 6.1 — Implementar cliente HTTP para n8n
**Veredicto:** COMPLETED ✅
