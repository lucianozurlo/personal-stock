# Devolución 64: Design — home-chat-orchestrator-contract

**Fecha**: 2026-06-25
**Spec**: home-chat-orchestrator-contract
**Fase**: Design (Requirements-first workflow)
**Veredicto**: ✅ APROBADO PARA REVISIÓN

---

## Resumen Ejecutivo

Se completó la generación del **design.md** para el spec **home-chat-orchestrator-contract**. Este documento define la arquitectura técnica completa del contrato de comunicación entre Django (frontend home/chat) y el orquestador n8n para Personal Stock MVP 1.

El diseño incluye:

- **Arquitectura de alto nivel** con 3 diagramas Mermaid (arquitectura, componentes, secuencia)
- **6 componentes principales** con interfaces Python completas
- **Data models** detallados (Request_Payload y Response_Payload)
- **Estrategia de validación** Django-side y n8n-side
- **Manejo de errores** exhaustivo con categorías y flujos
- **Testing strategy** (unit tests, integration tests, manual checklist)
- **Frontend integration** con cambios requeridos en app.js
- **Module structure** completa de carpetas Django
- **Implementation notes** con decisiones técnicas clave
- **Security, performance, deployment** considerations

---

## Contenido Generado

### Archivo creado

- `.kiro/specs/home-chat-orchestrator-contract/design.md` ✅

### Estructura del design.md (16 secciones)

1. **Overview**
   - Propósito y alcance del contrato
   - Stack técnico: Python/Django, DRF serializers, requests, n8n, Django session
   - Dependencias: usuarios-demo-perfiles-permisos ✅, base-django-login-home ✅

2. **Architecture** (3 diagramas Mermaid)
   - High-Level Architecture: flujo completo desde UI hasta n8n
   - Component Architecture: componentes Django y su interacción
   - Sequence Diagram: flujo detallado request/response con alternativas

3. **Components and Interfaces** (7 componentes)

   **ChatView** (`app/core/views.py`)
   - POST /api/chat/
   - Decorators: @login_required, @require_http_methods(["POST"]), @csrf_protect
   - Responsabilidades: recibir mensaje, gestionar conversationId, construir payload, validar, enviar a n8n, sanitizar HTML, retornar respuesta

   **ConversationIdManager** (`app/core/helpers/conversation.py`)
   - Generación: formato `conv-<timestamp>-<random>` (timestamp Unix base36 + random 6 chars [a-z0-9])
   - Almacenamiento: `request.session['conversationId']`
   - Métodos: generate_conversation_id(), get_or_create(session), reset(session)

   **UserObjectBuilder** (`app/core/helpers/user_object.py`)
   - Construcción de User_Object desde request.user
   - Reglas: userId=user.id, userEmail=user.email, userName=first_name+last_name (fallback: username)
   - Roles: vacío si perfil != "Usuario IC", sino from user.roles

   **PayloadSerializers** (`app/core/serializers/chat_serializers.py`)
   - RequestPayloadSerializer: valida schema de entrada Django-side
   - ResponsePayloadSerializer: valida schema de salida n8n→Django
   - UserObjectSerializer: valida User_Object structure
   - MetadataSerializer: valida metadata structure

   **N8nClient** (`app/core/clients/n8n_client.py`)
   - Envío HTTP POST a N8N_WEBHOOK_URL
   - Timeout: 30 segundos
   - Excepciones custom: N8nConnectionError, N8nTimeoutError, N8nInvalidResponseError
   - Manejo de errores: HTTP != 200, empty body, invalid JSON
   - Retorna errores a ChatView (no mock fallback)

   **HTMLSanitizer** (`app/core/helpers/html_sanitizer.py`)
   - Sanitización de HTML usando bleach library
   - Allow-list de tags seguros: p, strong, em, ul, ol, li, a, br, h1-h6, span, div
   - Allow-list de atributos: href (en a), class, id
   - Protocol restriction: href protocols limited to http, https, mailto (prevents javascript: XSS)
   - Procesa Response_Payload.output ANTES de retornar al frontend
   - Defense in depth: nunca confiar en sistemas externos (zero trust)

4. **Data Models**
   - Request_Payload schema completo con tabla de field descriptions
   - Response_Payload schema completo con tabla de field descriptions
   - Error Response schema
   - Ejemplos JSON reales

5. **Validation Strategy**
   - **Django-side (4 capas)**: request body parsing → user session → payload construction → schema validation
   - **n8n-side (9 validaciones)**: per Requirement 3, valida todos los campos requeridos
   - Defense in depth: ambas capas validan independientemente

6. **Error Handling**
   - Categorías: Client Errors (4xx), Server Errors (5xx), n8n Errors
   - Diagrama de flujo de error handling
   - Mensajes user-facing en español
   - Error logging con contexto (user_id, conversation_id, query, error_type)

7. **Testing Strategy**
   - **Unit tests** para cada componente (ConversationIdManager, UserObjectBuilder, Serializers, N8nClient, HTMLSanitizer)
   - **Integration tests** (full request flow, session persistence, error scenarios)
   - **Manual testing checklist** (16 items)

8. **Frontend Integration**
   - Cambios requeridos en templates/js/app.js
   - Reemplazo de llamadas directas a n8n por /api/chat/
   - Eliminación de "benja" hardcodeado
   - Frontend request format con fetch() y CSRF token
   - Frontend response handling con renderAssistantContent()
   - Error display

9. **Module Structure**
   - Estructura completa de carpetas Django
   - app/core/views.py, helpers/, serializers/, clients/, contracts/
   - app/tests/ con test files
   - URL configuration: path('api/chat/', views.chat_view)

10. **Implementation Notes**
    - ConversationId generation: formato detallado, uniqueness, storage, lifecycle
    - User_Object construction rules por campo
    - Django-side vs n8n-side validation: por qué ambos
    - n8n unavailable handling: returns clear error (503 Service Unavailable), no mock in this spec
    - Timeout configuration: 30s rationale
    - HTML rendering en MVP 1: solo true, campo presente para futuro
    - Dependency on memoria-feedback-correcciones: integration point definido

11. **Security Considerations**
    - Sensitive data exclusion: passwords, SECRET_KEY, API keys
    - CSRF protection con @csrf_protect (REQUIRED, NOT @csrf_exempt)
    - Authentication con @login_required
    - HTML sanitization: Django MUST sanitize using bleach (zero trust external systems)
    - Protocol restriction: href attributes limited to http, https, mailto (prevents javascript: XSS)
    - Input validation Django y n8n
    - Rate limiting (futuro, diseño ya soporta)

12. **Performance Considerations**
    - ConversationId generation: O(1), negligible
    - User_Object construction: O(1) + O(roles), optimización con prefetch_related
    - Request_Payload validation: O(fields), ~1ms
    - HTTP to n8n: bottleneck es n8n processing, no Django
    - Database impact: ~2-4 queries per request

13. **Future Evolution**
    - Memory Context en Request_Payload
    - Streaming responses con WebSocket
    - Agent routing metadata
    - Response formats (Markdown, plain text)
    - Trazabilidad automática
    - Advanced error recovery
    - Caching layer
    - Rate limiting per-user

14. **Dependencies and Integration Points**
    - Upstream: usuarios-demo-perfiles-permisos ✅, base-django-login-home ✅
    - Downstream: acciones-trazabilidad-metricas, rag-mails-dataset-permissions, trigger-comunicaciones-email
    - n8n workflow structure esperada (7 pasos)

15. **Deployment Considerations**
    - Environment variables: DJANGO_SECRET_KEY, DATABASE_URL, N8N_WEBHOOK_URL, N8N_TIMEOUT
    - Local development setup: n8n instance REQUIRED for testing webhook flow
    - n8n setup: crear webhook workflow (6 pasos, sin mock responses)
    - Production considerations (futuro): scale, security, monitoring, reliability

16. **Appendix**
    - Complete ChatView implementation outline (código completo)
    - Example test case (3 test methods)

---

## Decisiones Técnicas Clave

### ✅ Decisión 1: ConversationId en Django session (server-side)

- **Implementación**: `request.session['conversationId']` con clase ConversationIdManager
- **Formato**: `conv-<timestamp>-<random>` (timestamp Unix base36 + random 6 chars [a-z0-9])
- **Beneficios**: sobrevive entre pestañas, dispositivos (si sesión auth), refrescos; NO mezcla con localStorage browser
- **Lifecycle**: generado on first request, reused in same session, reset con "Nueva conversación"

### ✅ Decisión 2: User_Object completo en payload

- **Implementación**: UserObjectBuilder construye objeto completo desde request.user
- **Campos**: userId (number), userEmail (string), userName (string display), profile (enum), roles (array), memoryEnabled (boolean)
- **Rationale**: n8n NO necesita acceder a BD Django; mejor seguridad y simplicidad

### ✅ Decisión 3: Validación dual (Django-side y n8n-side)

- **Django-side**: RequestPayloadSerializer valida antes de enviar (fail fast, clear errors, reduce n8n load)
- **n8n-side**: Validation node per Requirement 3 (protege contra direct webhook calls, contract compliance)
- **Rationale**: defense in depth, ambos layers independientes

### ✅ Decisión 4: No mock fallback en este spec

- **Implementación**: Cuando n8n no disponible, retornar error claro (503 Service Unavailable)
- **Per requirements.md Conflict 4**: mock NO en este spec, implementado en otro spec si necesario
- **Decisión logic**: try N8nClient(), except → retornar error 503
- **Rationale**: separación de responsabilidades, claridad de errores

### ✅ Decisión 5: Timeout 30 segundos

- **Implementación**: requests.post(timeout=30) en N8nClient
- **Rationale**: balance UX (no muy largo) con agent processing time (RAG, LLM)
- **Frontend**: typing indicator while waiting, error si timeout

### ✅ Decisión 6: HTML only en MVP 1

- **Implementación**: html_render siempre true, output contiene HTML sanitizado
- **Frontend**: renderAssistantContent() de cs-chat-rag
- **Futuro**: campo presente para html_render=false (plain text/Markdown)
- **Security**: Django sanitiza HTML usando bleach (defense in depth, zero trust external systems)

### ✅ Decisión 7: Serializers DRF para validación Django-side

- **Implementación**: RequestPayloadSerializer, ResponsePayloadSerializer con rest_framework
- **Beneficios**: type checking, field validation, error messages claros, schema auto-documentado
- **Alternativa descartada**: validación manual con if/elif (menos mantenible)

### ✅ Decisión 8: CSRF protection explícita

- **Implementación**: @csrf_protect decorator en ChatView (NO @csrf_exempt)
- **Frontend**: X-CSRFToken header con token desde cookie (REQUIRED)
- **Rationale**: mejor seguridad con session auth, protección consistente contra CSRF

### ✅ Decisión 9: HTMLSanitizer con bleach

- **Implementación**: HTMLSanitizer.sanitize() procesa output ANTES de retornar al frontend
- **Biblioteca**: bleach con allow-list de tags y atributos seguros
- **Protocol restriction**: href protocols limited to http, https, mailto (prevents javascript: XSS)
- **Rationale**: zero trust external systems, defense in depth, prevención de XSS

---

## Diagramas Incluidos

### Diagrama 1: High-Level Architecture

- Flujo completo: User → app.js → ChatView → Session → UserObjectBuilder → PayloadValidator → N8nClient → n8n Webhook → Response
- Decisiones: conversationId generation if missing, validación Django-side

### Diagrama 2: Component Architecture

- Componentes Django: ChatView, SessionManager, UserObjectBuilder, PayloadValidator, N8nClient
- Django Session: Session Store con conversationId
- n8n Orchestrator: Webhook Endpoint, Payload Validator, Agent Router, Agent Response

### Diagrama 3: Sequence Diagram

- Participantes: User, app.js, ChatView, Session, UserObjectBuilder, PayloadValidator, N8nClient, n8n Webhook
- Flujo completo con alternativas: conversationId exists/missing, validation fails/succeeds, n8n available/unavailable

---

## Compatibilidad con Requirements

El design.md implementa TODOS los 10 requirements aprobados:

✅ **Requirement 1**: Request_Payload structure → UserObjectBuilder + ConversationIdManager
✅ **Requirement 2**: Response_Payload structure → ResponsePayloadSerializer
✅ **Requirement 3**: Validación Django-side → RequestPayloadSerializer (+ n8n-side documentado)
✅ **Requirement 4**: ConversationId en session → ConversationIdManager con session storage
✅ **Requirement 5**: Envío a n8n → N8nClient.send() con POST, timeout 30s
✅ **Requirement 6**: Procesamiento respuesta → ResponsePayloadSerializer + frontend integration
✅ **Requirement 7**: Error handling → N8nClientError hierarchy + error flow diagram
✅ **Requirement 8**: Construcción User_Object → UserObjectBuilder.build()
✅ **Requirement 9**: Dependencia memoria → integration point documentado en Implementation Notes
✅ **Requirement 10**: html_render MVP 1 → documentado en Implementation Notes + Future Evolution

---

## Estructura de Módulos Django

```
app/
├── core/
│   ├── views.py                          # ChatView POST /api/chat/
│   ├── urls.py                           # path('api/chat/', views.chat_view)
│   ├── helpers/
│   │   ├── __init__.py
│   │   ├── conversation.py               # ConversationIdManager
│   │   ├── user_object.py                # UserObjectBuilder
│   │   └── html_sanitizer.py             # HTMLSanitizer
│   ├── serializers/
│   │   ├── __init__.py
│   │   └── chat_serializers.py           # Request/Response/User/Metadata serializers
│   ├── clients/
│   │   ├── __init__.py
│   │   └── n8n_client.py                 # N8nClient + custom exceptions
│   └── contracts/
│       ├── __init__.py
│       └── n8n_user_payload.py           # TypedDict definitions (update existing)
└── tests/
    ├── test_conversation.py              # ConversationIdManager tests
    ├── test_user_object.py               # UserObjectBuilder tests
    ├── test_serializers.py               # Serializer tests
    ├── test_n8n_client.py                # N8nClient tests
    ├── test_html_sanitizer.py            # HTMLSanitizer tests
    └── test_chat_integration.py          # Integration tests
```

---

## Cambios en Frontend (app.js)

### OLD (cs-chat-rag)

```javascript
const N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/...';
const CHAT_USER_ID = "benja";
fetch(N8N_WEBHOOK_URL, { ... });
```

### NEW (Personal Stock)

```javascript
const CHAT_API_URL = "/api/chat/";
// No hardcoded user — viene de Django session

async function sendMessage(query, agentType = "auto") {
  const response = await fetch(CHAT_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    credentials: "same-origin",
    body: JSON.stringify({ query, agentType }),
  });

  const data = await response.json();

  if (data.error) {
    displayError(data.error);
  } else {
    renderAssistantMessage(data.output, data.metadata);
    console.log("Agent metadata:", data.metadata);
  }
}
```

---

## Environment Variables

```bash
# Required
DJANGO_SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
N8N_WEBHOOK_URL=http://localhost:5678/webhook/personal-stock-orchestrator

# Optional
N8N_TIMEOUT=30
```

---

## Testing Coverage

### Unit Tests (7 componentes)

1. ConversationIdManager: ID generation, base36, random uniqueness, session storage, reset
2. UserObjectBuilder: complete user data, fallback username, roles logic per profile, all profiles, memoryEnabled
3. RequestPayloadSerializer: valid payload, missing fields, invalid types, conversationId format, agentType fallback
4. ResponsePayloadSerializer: valid response, missing metadata, invalid types
5. N8nClient: success, timeout, connection error, non-200, empty body, invalid JSON
6. HTMLSanitizer: safe tags pass, unsafe tags removed, script tags blocked, attributes filtered, XSS prevention

### Integration Tests (3 scenarios)

1. Full request flow: user auth → POST → conversationId gen → User_Object → payload → n8n → sanitize HTML → response
2. Session persistence: first request gen, second reuse, reset new
3. Error scenarios: unauth 401, invalid JSON 400, missing query 400, timeout 504, n8n unavailable 503

### Manual Testing (16 items)

- Login different profiles
- Submit query verify conversationId
- Second query same conversationId
- Nueva conversación new conversationId
- Test n8n running (real webhook)
- Test n8n stopped (proper error handling)
- Verify User_Object data
- Roles empty non-IC
- Roles populated IC
- Invalid agentType fallback
- Error messages display
- HTML output renders

---

## Open Questions (NINGUNA)

Todas las decisiones fueron resueltas durante requirements phase. Design implementa las decisiones aprobadas.

---

## Assumptions

1. **Session backend configurado** (per base-django-login-home) ✅
2. **n8n puede no estar disponible** (error 503 retornado, no mock fallback) ✅
3. **User siempre autenticado** al acceder /api/chat/ (@login_required) ✅
4. **5 profiles exactos** per usuarios-demo-perfiles-permisos ✅
5. **Roles solo para Usuario IC** per usuarios-demo-perfiles-permisos Requirement 4 ✅
6. **HTML from n8n es untrusted** (Django sanitiza con bleach, zero trust external systems) ✅

---

## Constraints de MVP 1

1. **Solo HTML responses** (html_render: true) — plain text/Markdown en futuro MVP
2. **Local deployment** — no optimizado para 20k usuarios
3. **Synchronous** — no streaming, no async processing
4. **No caching** — cada request hits n8n
5. **No rate limiting** — protección contra abuse en futuro MVP

---

## Próximos Pasos

1. **Esperando aprobación explícita del usuario** antes de continuar
2. Una vez aprobado, proceder a generar **tasks.md** (siguiente fase del workflow requirements-first)
3. El tasks.md dividirá el diseño en:
   - Tareas atómicas implementables
   - Subtareas por componente
   - Orden de implementación
   - Criterios de aceptación por tarea
   - Testing checkpoints

---

## Conclusión

El design.md del spec **home-chat-orchestrator-contract** está completo y cumple con:

- ✅ Arquitectura técnica detallada con 3 diagramas Mermaid
- ✅ 6 componentes principales con interfaces Python completas
- ✅ Data models exhaustivos (Request_Payload y Response_Payload)
- ✅ Estrategia de validación dual (Django-side y n8n-side)
- ✅ Error handling con categorías, flujos y mensajes user-facing
- ✅ Testing strategy (unit, integration, manual)
- ✅ Frontend integration con cambios específicos en app.js
- ✅ Module structure completa de carpetas Django
- ✅ Implementation notes con decisiones técnicas clave
- ✅ Security, performance, deployment considerations
- ✅ Compatibilidad con todos los 10 requirements aprobados
- ✅ Dependencias upstream satisfechas (usuarios-demo ✅, base-django ✅)

**Estado**: ✅ LISTO PARA APROBACIÓN

**Requiere acción del usuario**: Aprobación explícita para proceder a la fase de tasks.md

**Fecha**: 2026-06-25
**Veredicto**: ✅ APROBADO PARA REVISIÓN
