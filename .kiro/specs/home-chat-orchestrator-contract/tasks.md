# Implementation Plan: Home Chat Orchestrator Contract

## Overview

Este plan implementa el contrato de comunicación entre Django home/chat y el orquestador n8n. La implementación sigue un orden lógico: helpers → serializers → client → view → frontend → tests.

**CRITICAL: Execution Mode**

Implementation is SERIALIZED, not parallel:

- One subtask per Claude Code session
- Strict numeric order: 1.1 → 1.2 → 2.1 → 2.2 → 2.3 → ... → 13.1
- NO parallel execution, even if Task Dependency Graph shows waves
- The wave structure is for reference only, showing logical dependencies

**Stack:**

- Python/Django (backend)
- Django REST Framework (serializers)
- requests library (HTTP client)
- bleach library (HTML sanitization)
- vanilla JS (frontend)

**Dependencias:**

- `usuarios-demo-perfiles-permisos`: User model con perfil, roles, memoria_habilitada
- `base-django-login-home`: autenticación, sesión, templates

## Tasks

### 1. Setup: Dependencias y estructura de directorios

- [x] 1.1 Agregar dependencias al proyecto
  - Agregar `djangorestframework` a `app/requirements.txt`
  - Agregar `requests` a `app/requirements.txt`
  - Agregar `bleach` a `app/requirements.txt`
  - Instalar dependencias: `pip install -r app/requirements.txt`
  - Verificar que `N8N_WEBHOOK_URL` ya existe en `.env.example`
  - _Requirements: Requirement 5 (requests), Requirement 6 (DRF), Component 6 (bleach)_

- [x] 1.2 Crear estructura de directorios para componentes
  - Crear directorio `app/core/helpers/`
  - Crear `app/core/helpers/__init__.py`
  - Crear directorio `app/core/serializers/`
  - Crear `app/core/serializers/__init__.py`
  - Crear directorio `app/core/clients/`
  - Crear `app/core/clients/__init__.py`
  - Verificar que `app/core/contracts/` ya existe
  - _Requirements: Design - Module Structure_

### 2. Implementar ConversationIdManager (Component 2)

- [x] 2.1 Implementar generación de conversationId
  - Crear archivo `app/core/helpers/conversation.py`
  - Implementar función `_to_base36(number: int) -> str` para conversión base36
  - Implementar `ConversationIdManager.generate_conversation_id()` con formato `conv-<timestamp>-<random>`
  - Timestamp: Unix timestamp en base36
  - Random: 6 caracteres alfanuméricos [a-z0-9]
  - _Requirements: Requirement 4 AC1_

- [x] 2.2 Implementar gestión de conversationId en sesión
  - Implementar `ConversationIdManager.get_or_create(session)` para obtener o crear ID
  - Implementar `ConversationIdManager.reset(session)` para resetear ID
  - Usar `SESSION_KEY = 'conversationId'` para storage
  - Marcar `session.modified = True` después de modificar
  - _Requirements: Requirement 4 AC2, AC3, AC4, AC5_

- [x] 2.3 Escribir tests unitarios para ConversationIdManager
  - Crear archivo `app/core/tests/test_conversation.py`
  - Test: formato de ID generado (`conv-<timestamp>-<random>`)
  - Test: conversión base36 correcta
  - Test: unicidad de random suffix
  - Test: get_or_create genera ID si no existe
  - Test: get_or_create reutiliza ID existente
  - Test: reset genera nuevo ID
  - _Requirements: Design - Testing Strategy_

### 3. Implementar UserObjectBuilder (Component 3)

- [x] 3.1 Implementar construcción de User_Object
  - Crear archivo `app/core/helpers/user_object.py`
  - Definir `UserObject` TypedDict con campos: userId, userEmail, userName, profile, roles, memoryEnabled
  - Implementar `UserObjectBuilder.build(user)` que extrae datos del User model
  - userId: `user.id` (int)
  - userEmail: `user.email` (str)
  - userName: `f"{user.first_name} {user.last_name}".strip()` con fallback a `user.username`
  - profile: `user.perfil` (str)
  - roles: lista de roles SOLO si perfil == "Usuario IC", sino lista vacía
  - memoryEnabled: `user.memoria_habilitada` (bool)
  - _Requirements: Requirement 8 AC1-7_

- [x] 3.2 Escribir tests unitarios para UserObjectBuilder
  - Crear archivo `app/core/tests/test_user_object.py`
  - Test: construcción completa con todos los campos
  - Test: fallback de userName cuando first_name vacío
  - Test: roles vacíos para perfil != "Usuario IC"
  - Test: roles poblados para perfil "Usuario IC"
  - Test: todos los 5 perfiles válidos
  - Test: memoryEnabled true y false
  - _Requirements: Design - Testing Strategy_

### 4. Implementar HTMLSanitizer (Component 6)

- [x] 4.1 Implementar sanitización de HTML
  - Crear archivo `app/core/helpers/html_sanitizer.py`
  - Implementar `HTMLSanitizer.sanitize(html_string: str) -> str`
  - ALLOWED_TAGS: p, strong, em, ul, ol, li, a, br, h1-h6, span, div
  - ALLOWED_ATTRIBUTES: a[href], \*[class, id]
  - Restricción de protocolos: http, https, mailto (previene javascript: XSS)
  - Usar `bleach.clean()` con strip=True
  - Usar `bleach.linkify()` para limpiar URLs en href
  - Manejar empty string → return ''
  - _Requirements: Design - Component 6_

- [x] 4.2 Escribir tests unitarios para HTMLSanitizer
  - Crear archivo `app/core/tests/test_html_sanitizer.py`
  - Test: tags permitidos pasan sin cambios
  - Test: tags no permitidos se remueven
  - Test: script tags bloqueados
  - Test: event handlers (onclick, onerror) bloqueados
  - Test: javascript: protocol en href bloqueado
  - Test: http/https/mailto protocols permitidos
  - Test: atributos no permitidos removidos
  - Test: empty string retorna empty string
  - _Requirements: Design - Testing Strategy_

### 5. Implementar PayloadSerializers (Component 4)

- [x] 5.1 Implementar serializers para validación Django-side
  - Crear archivo `app/core/serializers/chat_serializers.py`
  - Implementar `UserObjectSerializer` con campos: userId (int), userEmail (email), userName (str), profile (choice), roles (list), memoryEnabled (bool)
  - Implementar `RequestPayloadSerializer` con campos: conversationId, query, timestamp, user, agentType
  - Validación conversationId: debe empezar con 'conv-' y tener formato 'conv-<timestamp>-<random>'
  - Validación agentType: si no es válido ('auto', 'rag-mails', 'trigger-comunicaciones'), fallback a 'auto'
  - Implementar `MetadataSerializer` con campos: agent_used, execution_time_ms, records_found (nullable)
  - Implementar `ResponsePayloadSerializer` con campos: conversationId, output, html_render, metadata, error (optional)
  - _Requirements: Requirement 3, Design - Component 4_

- [x] 5.2 Escribir tests unitarios para serializers
  - Crear archivo `app/core/tests/test_serializers.py`
  - Test RequestPayloadSerializer: payload válido pasa
  - Test RequestPayloadSerializer: campos requeridos faltantes fallan
  - Test RequestPayloadSerializer: tipos incorrectos fallan
  - Test RequestPayloadSerializer: conversationId inválido falla
  - Test RequestPayloadSerializer: agentType inválido → fallback 'auto'
  - Test RequestPayloadSerializer: profile inválido falla
  - Test ResponsePayloadSerializer: payload válido pasa
  - Test ResponsePayloadSerializer: metadata faltante falla
  - _Requirements: Design - Testing Strategy_

### 6. Implementar N8nClient (Component 5)

- [x] 6.1 Implementar cliente HTTP para n8n
  - Crear archivo `app/core/clients/n8n_client.py`
  - Definir excepciones: `N8nClientError` (base), `N8nConnectionError`, `N8nTimeoutError`, `N8nInvalidResponseError`
  - Implementar `N8nClient.__init__(webhook_url)` que obtiene URL de `os.environ.get('N8N_WEBHOOK_URL')`
  - Implementar `N8nClient.send(payload)` con timeout de 30 segundos
  - Manejar status != 200 → `N8nConnectionError`
  - Manejar body vacío → `N8nInvalidResponseError`
  - Manejar JSON inválido → `N8nInvalidResponseError`
  - Manejar timeout → `N8nTimeoutError`
  - Manejar connection error → `N8nConnectionError`
  - _Requirements: Requirement 5, Requirement 7, Design - Component 5_

- [x] 6.2 Escribir tests unitarios para N8nClient
  - Crear archivo `app/core/tests/test_n8n_client.py`
  - Test: request exitoso retorna response_data
  - Test: timeout lanza N8nTimeoutError
  - Test: connection error lanza N8nConnectionError
  - Test: status != 200 lanza N8nConnectionError
  - Test: body vacío lanza N8nInvalidResponseError
  - Test: JSON inválido lanza N8nInvalidResponseError
  - Test: N8N_WEBHOOK_URL no configurada lanza ValueError
  - Usar `unittest.mock` para simular requests.post
  - _Requirements: Design - Testing Strategy_

### 7. Checkpoint - Componentes individuales completos

- [x] 7.1 Verificar que todos los helpers, serializers y client están implementados
  - Verificar que todos los tests unitarios pasan: `python app/manage.py test core.tests.test_conversation core.tests.test_user_object core.tests.test_html_sanitizer core.tests.test_serializers core.tests.test_n8n_client`
  - Reportar resultados de la verificación punto por punto

### 8. Implementar ChatView (Component 1)

- [x] 8.1 Implementar endpoint POST /api/chat/
  - Crear función `chat_view(request)` en `app/core/views.py`
  - Decoradores: `@login_required`, `@require_http_methods(["POST"])`, `@csrf_protect`
  - Parsear request.body como JSON
  - Extraer `query` (required) y `agentType` (optional, default 'auto')
  - Validar query no vacío, sino retornar 400
  - _Requirements: Requirement 5, Design - Component 1_

- [x] 8.2 Integrar ConversationIdManager en ChatView
  - Importar `ConversationIdManager` desde `core.helpers.conversation`
  - Llamar `ConversationIdManager.get_or_create(request.session)` para obtener conversationId
  - _Requirements: Requirement 4_

- [x] 8.3 Integrar UserObjectBuilder en ChatView
  - Importar `UserObjectBuilder` desde `core.helpers.user_object`
  - Llamar `UserObjectBuilder.build(request.user)` para construir user_object
  - _Requirements: Requirement 8_

- [x] 8.4 Construir y validar Request_Payload en ChatView
  - Construir `request_payload` dict con: conversationId, query, timestamp (ISO 8601), user (user_object), agentType
  - Importar `RequestPayloadSerializer`
  - Validar payload con serializer
  - Si inválido, retornar JsonResponse con error 400
  - _Requirements: Requirement 1, Requirement 3_

- [x] 8.5 Enviar payload a n8n y manejar respuesta en ChatView
  - Importar `N8nClient` y excepciones
  - Crear instancia de `N8nClient()`
  - Llamar `client.send(validated_payload)` en try/except
  - Manejar `N8nTimeoutError` → JsonResponse 504 con mensaje user-friendly
  - Manejar `N8nConnectionError` → JsonResponse 503 con mensaje de error
  - Manejar `N8nInvalidResponseError` → JsonResponse 502
  - Manejar `ValueError` (N8N_WEBHOOK_URL no configurada) → JsonResponse 503
  - Loggear todos los errores con contexto (user_id, conversation_id, query, error_type)
  - _Requirements: Requirement 5, Requirement 7_

- [x] 8.6 Sanitizar HTML y validar Response_Payload en ChatView
  - Importar `HTMLSanitizer` desde `core.helpers.html_sanitizer`
  - Sanitizar `response_data['output']` con `HTMLSanitizer.sanitize()`
  - Importar `ResponsePayloadSerializer`
  - Validar response_data con serializer
  - Si inválido, retornar JsonResponse 502 con error
  - Si válido, retornar JsonResponse 200 con validated_data
  - _Requirements: Requirement 6, Design - Component 6 (defense in depth)_

- [x] 8.7 Agregar logging completo en ChatView
  - Importar `logging` y crear logger: `logger = logging.getLogger(__name__)`
  - Loggear errores con `logger.error()` incluyendo context extra
  - Loggear excepciones inesperadas con `logger.exception()`
  - _Requirements: Design - Error Logging_

- [x] 8.8 Escribir tests de integración para ChatView
  - Crear archivo `app/core/tests/test_chat_integration.py`
  - Test: usuario autenticado puede enviar query
  - Test: conversationId se genera en primera request
  - Test: conversationId se reutiliza en segunda request
  - Test: usuario no autenticado recibe 401/302
  - Test: query vacío recibe 400
  - Test: JSON inválido recibe 400
  - Test: n8n timeout recibe 504
  - Test: n8n unavailable recibe 503
  - Usar `unittest.mock` para simular N8nClient
  - _Requirements: Design - Testing Strategy_

### 9. Agregar ruta /api/chat/ a URL routing

- [x] 9.1 Agregar endpoint a core/urls.py
  - Abrir `app/core/urls.py`
  - Importar `chat_view` desde views
  - Agregar `path('api/chat/', views.chat_view, name='chat')` a urlpatterns
  - Verificar que la ruta es accesible: debe responder 401/302 si no autenticado
  - _Requirements: Design - URL Configuration_

### 10. Checkpoint - Backend completo

- [x] 10.1 Verificar integración completa del backend
  - Ejecutar todos los tests: `python app/manage.py test core.tests`
  - Verificar que N8N_WEBHOOK_URL está en `.env.example`
  - Iniciar servidor Django: `python app/manage.py runserver`
  - Verificar que endpoint `/api/chat/` existe (debe requerir autenticación)
  - Reportar resultados de la verificación punto por punto

### 11. Integración Frontend (templates/js/app.js)

- [x] 11.1 Modificar app.js para usar endpoint Django
  - Abrir archivo `templates/js/app.js` (asumiendo que existe de cs-chat-rag)
  - Cambiar URL de n8n directo a Django endpoint: `const CHAT_API_URL = '/api/chat/'`
  - Eliminar constante `N8N_WEBHOOK_URL` si existe
  - Eliminar constante `CHAT_USER_ID = "benja"` hardcodeada
  - _Requirements: Design - Frontend Integration_

- [x] 11.2 Implementar función getCsrfToken en app.js
  - Crear función `getCsrfToken()` que extrae CSRF token de cookie 'csrftoken'
  - Iterar por `document.cookie.split(";")` buscando 'csrftoken'
  - Retornar valor decodificado con `decodeURIComponent()`
  - _Requirements: Design - CSRF Token Handling_

- [x] 11.3 Modificar sendMessage para incluir CSRF token
  - Modificar función `sendMessage(query, agentType = "auto")`
  - Usar `fetch('/api/chat/', { method: 'POST', ... })`
  - Headers: `'Content-Type': 'application/json'`, `'X-CSRFToken': getCsrfToken()`
  - Credentials: `'same-origin'` para incluir session cookie
  - Body: `JSON.stringify({ query, agentType })`
  - _Requirements: Design - Frontend Request Format_

- [x] 11.4 Manejar Response_Payload en frontend
  - Verificar que `response.ok` antes de parsear JSON
  - Si no ok, lanzar error con status
  - Parsear respuesta: `const data = await response.json()`
  - Si `data.error` existe, llamar `displayError(data.error)`
  - Si exitoso, llamar `renderAssistantMessage(data.output, data.metadata)`
  - Loggear metadata a console: `console.log('Agent metadata:', data.metadata)`
  - _Requirements: Requirement 6, Design - Frontend Response Handling_

- [x] 11.5 Implementar función displayError en app.js
  - Crear función `displayError(errorMessage)` si no existe
  - Crear div con clase 'assistant-message error-message'
  - Contenido: `<p><strong>Error</strong></p><p>${errorMessage}</p>`
  - Agregar a chatContainer
  - Llamar `removeTypingIndicator()` si existe
  - Guardar en history con `isError: true`
  - _Requirements: Design - Error Display_

### 12. Testing Manual End-to-End

- [x] 12.1 Preparar entorno de testing
  - Verificar que n8n está corriendo en `http://localhost:5678` (si se va a testear con n8n real)
  - Cargar usuarios demo: `python app/manage.py load_demo_users`
  - Iniciar servidor Django: `python app/manage.py runserver`
  - Abrir navegador en `http://localhost:8000`

- [x] 12.2 Ejecutar checklist de testing manual
  - Login como "Administrador" (comustock.ci@gmail.com / admin123)
  - Enviar query: "Hola, ¿cómo estás?" y verificar conversationId en session (DevTools)
  - Enviar segunda query y verificar que conversationId NO cambió
  - Verificar en Network tab que request a `/api/chat/` incluye X-CSRFToken header
  - Verificar que response tiene estructura: conversationId, output, html_render, metadata
  - Logout y verificar que endpoint `/api/chat/` requiere autenticación
  - Login como "Usuario IC" y verificar que roles se envían en payload
  - Login como "Usuario" (no IC) y verificar que roles está vacío
  - Si n8n NO está corriendo, verificar que se muestra error claro 503
  - Verificar que HTML en output está sanitizado (no script tags, no onclick)
  - _Requirements: Design - Manual Testing Checklist_

- [x] 12.3 Verificar logs y trazabilidad
  - Verificar en terminal Django que errores se loggean correctamente
  - Verificar que errores incluyen contexto: user_id, conversation_id, error_type
  - Verificar en browser console que metadata se loggea correctamente
  - _Requirements: Design - Error Logging_

### 13. Documentación y cierre

- [x] 13.1 Crear devolución final
  - Crear archivo `docs/devoluciones/66-tasks-home-chat-orchestrator-contract.md`
  - Fecha: 2026-06-25
  - Resumen ejecutivo: contrato Django ↔ n8n implementado con 7 componentes
  - Estructura: 13 tareas principales, todas MANDATORY (incluyendo tests)
  - Componentes: ConversationIdManager, UserObjectBuilder, HTMLSanitizer, PayloadSerializers, N8nClient, ChatView, Frontend Integration
  - Próximos pasos: implementar orquestador n8n, agentes RAG y Trigger Comunicaciones
  - Veredicto: READY FOR IMPLEMENTATION

## Notes

### Estructura de Implementación

El plan sigue un orden lógico que minimiza dependencias:

1. **Setup** (Tareas 1.x): Instalar dependencias y crear estructura
2. **Helpers independientes** (Tareas 2-4): ConversationIdManager, UserObjectBuilder, HTMLSanitizer (sin dependencias entre sí)
3. **Serializers** (Tarea 5): Validación de payloads (depende de estructura de datos)
4. **N8nClient** (Tarea 6): Cliente HTTP (solo depende de requests)
5. **ChatView** (Tarea 8): Vista que integra TODOS los componentes anteriores
6. **URL Routing** (Tarea 9): Conectar vista a ruta
7. **Frontend** (Tarea 11): Modificar app.js para usar endpoint Django
8. **Testing** (Tarea 12): Validación end-to-end manual

### Testing Tasks

**Unit Tests and Integration Tests** (tasks 2.3, 3.2, 4.2, 5.2, 6.2, 8.8):

- All test tasks are **MANDATORY**
- Unit tests validate individual components
- Integration tests (8.8) validate ChatView end-to-end flows
- Tests MUST pass before moving to production

**CRITICAL**: HTMLSanitizer tests (4.2) are especially important for security validation:

- Test javascript: protocol blocking
- Test script tag removal
- Test event handler removal (onclick, onerror)
- These tests validate XSS protection, which is critical for a security component

### Archivos Esperados

Por cada tarea principal, estos son los archivos esperados:

**Tarea 1 (Setup):**

- `app/requirements.txt` (modificado)
- `app/core/helpers/__init__.py` (creado)
- `app/core/serializers/__init__.py` (creado)
- `app/core/clients/__init__.py` (creado)

**Tarea 2 (ConversationIdManager):**

- `app/core/helpers/conversation.py` (creado)
- `app/core/tests/test_conversation.py` (creado)

**Tarea 3 (UserObjectBuilder):**

- `app/core/helpers/user_object.py` (creado)
- `app/core/tests/test_user_object.py` (creado)

**Tarea 4 (HTMLSanitizer):**

- `app/core/helpers/html_sanitizer.py` (creado)
- `app/core/tests/test_html_sanitizer.py` (creado)

**Tarea 5 (Serializers):**

- `app/core/serializers/chat_serializers.py` (creado)
- `app/core/tests/test_serializers.py` (creado)

**Tarea 6 (N8nClient):**

- `app/core/clients/n8n_client.py` (creado)
- `app/core/tests/test_n8n_client.py` (creado)

**Tarea 8 (ChatView):**

- `app/core/views.py` (modificado, agregar chat_view)
- `app/core/tests/test_chat_integration.py` (creado)

**Tarea 9 (URL Routing):**

- `app/core/urls.py` (modificado, agregar ruta /api/chat/)

**Tarea 11 (Frontend):**

- `templates/js/app.js` (modificado)

**Tarea 13 (Documentación):**

- `docs/devoluciones/65-tasks-home-chat-orchestrator-contract.md` (creado)

### Criterios de Aceptación Verificables

Cada tarea tiene criterios específicos y verificables:

- **Componentes individuales**: Implementación cumple con interface definida en design.md
- **Tests obligatorios**: Deben pasar con `python manage.py test`
- **ChatView**: Endpoint responde correctamente a requests válidos e inválidos
- **Frontend**: Requests incluyen CSRF token, respuestas se renderizan correctamente
- **Manual testing**: Checklist completo verificado

### Dependencias de Specs

Este spec requiere:

- `usuarios-demo-perfiles-permisos`: COMPLETED (User model existe)
- `base-django-login-home`: COMPLETED (autenticación, sesión, templates existen)

Este spec NO implementa:

- Orquestador n8n (workflows en n8n)
- Agentes específicos (rag-mails, trigger-comunicaciones)
- Trazabilidad completa (spec `acciones-trazabilidad-metricas`)
- Regla de precedencia memoria (spec `memoria-feedback-correcciones`)

### Conflictos Resueltos

Todos los conflictos de requirements.md fueron resueltos:

1. USERNAME_FIELD es email → userEmail (auth), userId (trazabilidad), userName (display)
2. Validación Django-side → validar ANTES de enviar a n8n
3. Memoria efectiva → transportar valor, lógica en otro spec
4. Contrato unificado → un solo webhook para todos los agentes
5. html_render en MVP 1 → siempre true, campo presente para futuro
6. User_Object completo → Django envía contexto completo

### No Mock en Este Spec

**IMPORTANTE**: Per Conflict 4 de requirements.md, este spec NO implementa mock de n8n cuando n8n no está disponible.

Cuando N8N_WEBHOOK_URL no configurada o n8n unavailable:

- Django retorna error claro: 503 Service Unavailable
- Mensaje: "Error conectando con n8n: ..."
- NO hay fallback, NO hay mock responses

Mock para desarrollo local sin n8n se implementa en otro spec si es necesario.

### Seguridad: Defense in Depth

**HTML Sanitization es CRÍTICA**:

- Django MUST sanitizar HTML de n8n con bleach antes de retornar a frontend
- Zero trust external systems: nunca confiar en salida de n8n
- HTMLSanitizer con allow-list de tags y attributes
- Restricción de protocolos: solo http, https, mailto (previene javascript: XSS)
- Frontend usa DOMPurify como capa adicional

**CSRF Protection**:

- ChatView usa `@csrf_protect` (NOT @csrf_exempt)
- Frontend MUST enviar X-CSRFToken header
- Session-based auth requiere CSRF protection

### Orden de Implementación Crítico

NO cambiar el orden de las tareas 2-8:

1. Helpers primero (2-4): sin dependencias entre sí
2. Serializers (5): depende de estructura de datos
3. N8nClient (6): depende solo de requests
4. ChatView (8): depende de TODO lo anterior

Frontend (11) puede modificarse en paralelo con backend si se prefiere.

## Task Dependency Graph

**Note**: This graph shows logical dependencies between tasks and potential parallelization opportunities. However, **implementation follows strict serialized execution** (one task per session in numeric order). The wave structure is for reference only.

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["2.1", "3.1", "4.1"] },
    { "id": 2, "tasks": ["2.2", "2.3", "3.2", "4.2", "5.1"] },
    { "id": 3, "tasks": ["5.2", "6.1"] },
    { "id": 4, "tasks": ["6.2", "7.1"] },
    { "id": 5, "tasks": ["8.1", "8.2"] },
    { "id": 6, "tasks": ["8.3", "8.4"] },
    { "id": 7, "tasks": ["8.5"] },
    { "id": 8, "tasks": ["8.6", "8.7"] },
    { "id": 9, "tasks": ["8.8", "9.1"] },
    { "id": 10, "tasks": ["10.1"] },
    { "id": 11, "tasks": ["11.1", "11.2"] },
    { "id": 12, "tasks": ["11.3", "11.4", "11.5"] },
    { "id": 13, "tasks": ["12.1"] },
    { "id": 14, "tasks": ["12.2", "12.3"] },
    { "id": 15, "tasks": ["13.1"] }
  ]
}
```
