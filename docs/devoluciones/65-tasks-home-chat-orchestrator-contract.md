# Devolución: Tasks para home-chat-orchestrator-contract

**Fecha:** 2026-06-25
**Spec:** home-chat-orchestrator-contract
**Workflow:** Requirements-First
**Estado:** READY FOR IMPLEMENTATION

---

## Resumen Ejecutivo

Se generó el tasks.md completo para el spec `home-chat-orchestrator-contract` que implementa el contrato de comunicación entre Django (frontend home/chat) y el orquestador n8n.

El plan de implementación consta de **13 tareas principales** organizadas en **16 waves de ejecución paralela** (solo para referencia de dependencias lógicas), con **todas las sub-tareas siendo MANDATORY**, incluyendo los tests unitarios e integración.

### Componentes Implementados

El tasks.md cubre la implementación de **7 componentes principales** del sistema:

1. **ConversationIdManager** (Component 2): Generación y gestión de IDs de conversación en Django session
2. **UserObjectBuilder** (Component 3): Construcción del objeto user desde request.user
3. **HTMLSanitizer** (Component 6): Sanitización HTML con bleach para prevenir XSS
4. **PayloadSerializers** (Component 4): Validación Django-side con DRF serializers
5. **N8nClient** (Component 5): Cliente HTTP para comunicación con webhook n8n
6. **ChatView** (Component 1): Vista Django que integra todos los componentes
7. **Frontend Integration** (templates/js/app.js): Modificaciones para consumir endpoint Django

---

## Estructura del Plan de Tareas

### Tareas Principales (13 grupos)

1. **Setup** (1.1-1.2): Dependencias y estructura de directorios
2. **ConversationIdManager** (2.1-2.3): Generación y gestión de conversationId
3. **UserObjectBuilder** (3.1-3.2): Construcción de User_Object
4. **HTMLSanitizer** (4.1-4.2): Sanitización HTML con bleach
5. **PayloadSerializers** (5.1-5.2): Validación de Request/Response payloads
6. **N8nClient** (6.1-6.2): Cliente HTTP para n8n
7. **Checkpoint Backend Individual** (7.1): Validación de componentes individuales
8. **ChatView** (8.1-8.8): Vista Django que integra todos los componentes
9. **URL Routing** (9.1): Agregar ruta /api/chat/
10. **Checkpoint Backend Completo** (10.1): Validación de integración completa
11. **Frontend Integration** (11.1-11.5): Modificar app.js para usar endpoint Django
12. **Testing Manual E2E** (12.1-12.3): Checklist de testing manual
13. **Documentación** (13.1): Devolución final

### Sub-tareas de Testing (MANDATORY)

Testing unitario para cada componente (todas MANDATORY):

- 2.3: Tests ConversationIdManager
- 3.2: Tests UserObjectBuilder
- 4.2: Tests HTMLSanitizer (CRITICAL para validación de seguridad XSS)
- 5.2: Tests Serializers
- 6.2: Tests N8nClient
- 8.8: Tests integración ChatView

**IMPORTANTE**: Todas las tareas de testing son MANDATORY, especialmente 4.2 (HTMLSanitizer tests) que valida protección XSS crítica para seguridad: javascript: protocol blocking, script tag removal, event handler removal.

---

## Orden de Implementación

**IMPORTANTE**: Aunque el grafo muestra waves de paralelización, la implementación real es SERIALIZADA: una subtarea por sesión en orden numérico estricto (1.1 → 1.2 → 2.1 → ...).

El plan sigue un orden lógico que **minimiza dependencias** y muestra **oportunidades de paralelización lógica** (solo para referencia):

```
Wave 0: Setup (dependencias + estructura)
  ↓
Wave 1-2: Helpers independientes (ConversationId, UserObject, HTMLSanitizer) en paralelo
  ↓
Wave 3: Serializers (depende de estructura de datos)
  ↓
Wave 4: N8nClient (depende de requests)
  ↓
Wave 5-9: ChatView (integra TODOS los componentes)
  ↓
Wave 10: Checkpoint backend
  ↓
Wave 11-12: Frontend (modifica app.js)
  ↓
Wave 13-14: Testing manual E2E
  ↓
Wave 15: Documentación
```

### Rationale del Orden

1. **Helpers primero** (waves 1-2): ConversationIdManager, UserObjectBuilder, HTMLSanitizer no dependen entre sí → pueden implementarse en paralelo
2. **Serializers después** (wave 3): necesitan conocer estructura de datos de helpers
3. **N8nClient independiente** (wave 4): solo depende de requests, puede hacerse en paralelo con serializers
4. **ChatView al final** (waves 5-9): integra TODO lo anterior, por eso va último en backend
5. **Frontend después de backend** (waves 11-12): necesita endpoint /api/chat/ funcionando

---

## Archivos que Se Crearán/Modificarán

### Archivos Nuevos (17)

**Helpers:**

- `app/core/helpers/__init__.py`
- `app/core/helpers/conversation.py` (ConversationIdManager)
- `app/core/helpers/user_object.py` (UserObjectBuilder)
- `app/core/helpers/html_sanitizer.py` (HTMLSanitizer)

**Serializers:**

- `app/core/serializers/__init__.py`
- `app/core/serializers/chat_serializers.py`

**Clients:**

- `app/core/clients/__init__.py`
- `app/core/clients/n8n_client.py`

**Tests (MANDATORY):**

- `app/core/tests/test_conversation.py`
- `app/core/tests/test_user_object.py`
- `app/core/tests/test_html_sanitizer.py`
- `app/core/tests/test_serializers.py`
- `app/core/tests/test_n8n_client.py`
- `app/core/tests/test_chat_integration.py`

**Documentación:**

- `docs/devoluciones/65-tasks-home-chat-orchestrator-contract.md` (este archivo)

### Archivos Modificados (3)

- `app/requirements.txt`: agregar djangorestframework, requests, bleach
- `app/core/views.py`: agregar función chat_view
- `app/core/urls.py`: agregar ruta /api/chat/
- `templates/js/app.js`: modificar para usar endpoint Django

---

## Dependencias Técnicas

### Nuevas Dependencias en requirements.txt

```python
djangorestframework  # Serializers para validación
requests            # Cliente HTTP para n8n
bleach              # Sanitización HTML
```

### Variables de Entorno

Ya existe en `.env.example`:

- `N8N_WEBHOOK_URL=http://localhost:5678/webhook-test/personal-stock-orchestrator`

No se requieren cambios en `.env.example`.

---

## Criterios de Aceptación por Componente

### 1. ConversationIdManager

- ✅ Genera IDs con formato `conv-<timestamp>-<random>`
- ✅ Almacena en Django session con key 'conversationId'
- ✅ Reutiliza ID existente en requests subsiguientes
- ✅ Reset genera nuevo ID

### 2. UserObjectBuilder

- ✅ Extrae userId, userEmail, userName del User model
- ✅ Fallback de userName cuando first_name vacío
- ✅ Roles vacíos para perfil != "Usuario IC"
- ✅ Roles poblados para perfil "Usuario IC"

### 3. HTMLSanitizer

- ✅ Allow-list de tags seguros (p, strong, em, ul, ol, li, a, br, h1-h6, span, div)
- ✅ Allow-list de attributes (a[href], \*[class, id])
- ✅ Restricción de protocolos: http, https, mailto (bloquea javascript:)
- ✅ Bloques script tags, event handlers, contenido malicioso

### 4. PayloadSerializers

- ✅ RequestPayloadSerializer valida estructura completa
- ✅ Validación de conversationId format
- ✅ Fallback de agentType inválido a "auto"
- ✅ ResponsePayloadSerializer valida metadata requerida

### 5. N8nClient

- ✅ Envía POST a N8N_WEBHOOK_URL con timeout 30s
- ✅ Lanza N8nTimeoutError si timeout
- ✅ Lanza N8nConnectionError si connection error
- ✅ Lanza N8nInvalidResponseError si body vacío o JSON inválido

### 6. ChatView

- ✅ Decoradores: @login_required, @require_http_methods(["POST"]), @csrf_protect
- ✅ Parsea request body como JSON
- ✅ Valida query no vacío
- ✅ Integra ConversationIdManager para obtener/crear ID
- ✅ Integra UserObjectBuilder para construir user_object
- ✅ Valida Request_Payload con RequestPayloadSerializer
- ✅ Envía a n8n con N8nClient
- ✅ Maneja errores (timeout 504, connection 503, invalid 502)
- ✅ Sanitiza HTML output con HTMLSanitizer
- ✅ Valida Response_Payload con ResponsePayloadSerializer
- ✅ Loggea errores con contexto

### 7. Frontend Integration

- ✅ URL cambiada a '/api/chat/'
- ✅ Eliminado "benja" hardcodeado
- ✅ Función getCsrfToken() implementada
- ✅ X-CSRFToken header incluido en requests
- ✅ Credentials: 'same-origin' para incluir session cookie
- ✅ Manejo de Response_Payload (output, metadata)
- ✅ displayError() implementado para errores

---

## Testing Strategy

### Tests Unitarios (MANDATORY)

Cada componente tiene tests unitarios dedicados:

- ConversationIdManager: formato, base36, session storage, reset
- UserObjectBuilder: campos, fallbacks, roles por perfil
- HTMLSanitizer: tags, attributes, XSS prevention (CRITICAL)
- Serializers: validación campos, tipos, formatos
- N8nClient: request/response, timeouts, errores

**Status:** MANDATORY - todas las tareas de testing son obligatorias

### Tests de Integración (MANDATORY)

Test completo del flujo ChatView:

- Usuario autenticado puede enviar query
- ConversationId se genera y reutiliza
- Usuario no autenticado recibe 401/302
- Query vacío recibe 400
- n8n timeout/unavailable reciben 504/503

**Status:** MANDATORY - obligatoria antes de producción

### Testing Manual E2E (Obligatorio - tareas 12.1-12.3)

Checklist completo de testing manual:

- Login con diferentes perfiles (Administrador, Usuario IC, Usuario)
- Verificar conversationId en session (DevTools)
- Verificar X-CSRFToken header en requests
- Verificar estructura Response_Payload
- Verificar roles según perfil
- Verificar errores cuando n8n unavailable
- Verificar HTML sanitizado (no scripts)
- Verificar logs en terminal Django

**Status:** Obligatorio antes de cerrar spec

---

## Seguridad: Puntos Críticos

### 1. HTML Sanitization (Defense in Depth)

**CRÍTICO**: Django MUST sanitizar HTML de n8n antes de retornar a frontend.

- Zero trust external systems: nunca confiar en output de n8n
- HTMLSanitizer con bleach library
- Allow-list approach: solo tags/attributes seguros
- Protocol restriction: href limitado a http, https, mailto (previene javascript: XSS)
- Frontend usa DOMPurify como capa adicional

### 2. CSRF Protection

- ChatView usa `@csrf_protect` (NOT @csrf_exempt)
- Frontend MUST enviar X-CSRFToken header
- Session-based auth requiere CSRF protection

### 3. Authentication

- `@login_required` en ChatView
- Endpoint /api/chat/ solo accesible para usuarios autenticados

### 4. Input Validation

- Serializers validan tipos y estructura
- Query debe ser non-empty string
- No SQL injection (usando ORM)

---

## Decisiones de Diseño Importantes

### 1. No Mock en Este Spec

**Per Conflict 4 de requirements.md**, este spec NO implementa mock de n8n.

Cuando N8N_WEBHOOK_URL no configurada o n8n unavailable:

- Django retorna error claro: 503 Service Unavailable
- Mensaje: "Error conectando con n8n: ..."
- NO hay fallback, NO hay mock responses

Mock para desarrollo local sin n8n se implementa en otro spec si es necesario.

### 2. html_render Siempre true en MVP 1

**Per Conflict 5 de requirements.md**, MVP 1 solo soporta HTML.

- Response_Payload field `html_render` siempre es `true`
- Campo presente para forward compatibility
- Plain text / Markdown support es evolución futura

### 3. Django-side Validation (Defense in Depth)

**Per Conflict 2 de requirements.md**, Django valida ANTES de enviar a n8n.

- Fail fast: no HTTP request si payload inválido
- Errores claros a frontend
- Reduce carga en n8n
- n8n también valida (defensa en profundidad)

### 4. Contrato Unificado para Todos los Agentes

**Per Conflict 4 de requirements.md**, un solo webhook para todos los agentes.

- Campo `agentType` o auto-detección de intención
- No múltiples webhooks
- Simplifica integración

### 5. Memoria Efectiva Transportada, No Definida

**Per Conflict 3 de requirements.md**, contrato transporta valor efectivo.

- Campo `memoryEnabled` viene de `user.memoria_habilitada` (actual)
- Lógica de precedencia (toggle UI vs BD) definida en spec `memoria-feedback-correcciones`
- Este spec solo transporta el valor, no define la lógica de negocio

---

## Dependencias de Specs

### Upstream (Requeridas ANTES de implementar)

**Status: AMBAS COMPLETAS** ✅

1. **usuarios-demo-perfiles-permisos**:
   - User model con campos: id, email, first_name, last_name, perfil, roles, memoria_habilitada
   - 5 perfiles: Administrador, Usuario IC, Heavy user, Macro, Usuario
   - Regla: roles solo para "Usuario IC"

2. **base-django-login-home**:
   - Autenticación funcionando
   - Session backend configurado
   - request.user poblado con User autenticado
   - Templates: home.html, app.js

### Downstream (Consumirán este contrato)

1. **acciones-trazabilidad-metricas**: Loggea Request/Response, usa conversationId
2. **rag-mails-dataset-permissions**: Recibe User_Object, retorna Response_Payload
3. **trigger-comunicaciones-email**: Recibe User_Object, retorna Response_Payload
4. **memoria-feedback-correcciones**: Provee memoryEnabled efectivo, usa conversationId

---

## Próximos Pasos

### Inmediato (Este Spec)

1. ✅ Tasks.md generado (DONE)
2. ✅ Devolución creada (este documento)
3. ⏳ **Pendiente**: User approval del tasks.md
4. ⏳ **Pendiente**: Implementación siguiendo tasks.md secuencialmente

### Después de Este Spec (Specs Dependientes)

1. **n8n Orchestrator Workflow**: Configurar webhook en n8n que reciba Request_Payload y retorne Response_Payload
2. **acciones-trazabilidad-metricas**: Implementar logging completo de requests/responses
3. **rag-mails-dataset-permissions**: Implementar agente RAG que consume contrato
4. **trigger-comunicaciones-email**: Implementar agente Trigger que consume contrato

### Testing E2E con n8n Real

Una vez implementado:

1. Configurar workflow básico en n8n con validación + respuesta mock
2. Ejecutar checklist manual (tarea 12.2)
3. Verificar logs y trazabilidad (tarea 12.3)

---

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

**Total waves:** 16
**Paralelización:** Wave structure shows logical dependencies only - actual implementation is SERIALIZED
**Orden crítico:** Wave N can only execute logically after completing all waves 0..N-1, but in practice tasks execute sequentially in numeric order

---

## Métricas del Plan

- **Tareas principales:** 13 grupos (1-13)
- **Sub-tareas totales:** 36
- **Sub-tareas MANDATORY:** 36 (todas, incluyendo tests)
- **Waves de ejecución:** 16 (solo para referencia de dependencias lógicas)
- **Componentes implementados:** 7
- **Archivos nuevos:** 17
- **Archivos modificados:** 3
- **Dependencias nuevas:** 3 (djangorestframework, requests, bleach)

---

## Veredicto Final

✅ **READY FOR IMPLEMENTATION**

El tasks.md generado:

- ✅ Cumple con TODOS los requirements del spec
- ✅ Implementa TODOS los componentes del design
- ✅ Sigue orden lógico que minimiza dependencias
- ✅ Define criterios de aceptación verificables para cada tarea
- ✅ Especifica archivos esperados por tarea
- ✅ TODAS las tareas son MANDATORY (incluyendo tests)
- ✅ Tests de HTMLSanitizer (4.2) son CRITICAL para seguridad XSS
- ✅ Incluye checkpoints de validación (tareas 7.1, 10.1)
- ✅ Incluye testing manual E2E obligatorio (tareas 12.x)
- ✅ Respeta decisiones de conflicts resueltos en requirements.md
- ✅ Documenta puntos críticos de seguridad
- ✅ Dependency graph válido con 16 waves (solo referencia lógica)
- ✅ Ejecución serializada: una tarea por sesión en orden numérico

**El spec está listo para comenzar implementación.**

---

**Fin de Devolución**
