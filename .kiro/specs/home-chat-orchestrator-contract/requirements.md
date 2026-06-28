# Requirements Document

## Introduction

Este spec define el contrato de comunicación entre Django home/chat y el orquestador n8n para Personal Stock MVP 1. El contrato establece el schema de entrada (payload que Django envía a n8n) y el schema de salida (respuesta que n8n devuelve a Django) para toda interacción conversacional.

El contrato unificado soporta todos los agentes del sistema (RAG de mails históricos, Trigger Comunicaciones, futuros) mediante un solo webhook. El orquestador n8n usa el campo `agentType` o la intención detectada para rutear la solicitud al agente correcto.

Este spec NO implementa:

- La lógica del orquestador n8n (configuración de workflows en n8n)
- Los agentes específicos (specs separados: `rag-mails-dataset-permissions`, `trigger-comunicaciones-email`)
- La trazabilidad completa (spec `acciones-trazabilidad-metricas`)
- La regla de precedencia toggle-UI vs BD para memoria (spec `memoria-feedback-correcciones`)

Este spec SÍ define:

- Payload de entrada desde Django a n8n (`Request_Payload`)
- Payload de salida desde n8n a Django (`Response_Payload`)
- Validaciones de estructura y campos requeridos
- Manejo de errores y casos edge

## Glossary

- **Django_Frontend**: Sistema Django que ejecuta templates `home.html` y `app.js` (frontend conversacional)
- **N8n_Orchestrator**: Webhook de n8n que recibe queries del frontend y deriva a agentes
- **Request_Payload**: Payload JSON enviado desde Django al webhook de n8n
- **Response_Payload**: Payload JSON devuelto desde n8n a Django
- **ConversationId**: Identificador único de sesión conversacional (formato: `conv-<timestamp>-<random>`)
- **User_Object**: Objeto JSON con datos del usuario autenticado (userId, userEmail, userName, profile, roles, memoryEnabled)
- **Metadata_Object**: Objeto JSON con información de trazabilidad (agent_used, execution_time_ms, records_found)
- **HTML_Render**: Indicador booleano que señala si `output` contiene HTML sanitizado (`true`) o plain text (`false`)
- **Agent_Type**: String que identifica el tipo de agente solicitado (`"rag-mails"`, `"trigger-comunicaciones"`, `"auto"`)
- **Memory_Context**: Historia conversacional previa incluida cuando `memoryEnabled=true`
- **Webhook_URL**: URL del webhook de n8n definida en variable de entorno `N8N_WEBHOOK_URL`

## Requirements

### Requirement 1: Definir estructura de Request_Payload

**User Story:** Como Django_Frontend, necesito enviar un payload estructurado al N8n_Orchestrator incluyendo query del usuario, contexto de sesión y datos del usuario autenticado, para que el orquestador derive la solicitud al agente correcto con permisos aplicados.

#### Acceptance Criteria

1. THE Request_Payload SHALL include the field `conversationId` as a string with format `conv-<timestamp>-<random>` WHERE timestamp is Unix timestamp in base36 AND random is 6-character alphanumeric string

2. THE Request_Payload SHALL include the field `query` as a non-empty string containing the user's message text

3. THE Request_Payload SHALL include the field `timestamp` as an ISO 8601 string representing the moment the query was created

4. THE Request_Payload SHALL include the field `user` as an object containing:
   - `userId` (number): Django user.id
   - `userEmail` (string): Django user.email (USERNAME_FIELD)
   - `userName` (string): Django user.first_name + " " + user.last_name
   - `profile` (string): one of "Administrador", "Usuario IC", "Heavy user", "Macro", "Usuario"
   - `roles` (array of strings): roles assigned to the user (e.g., ["Diseñador", "Desarrollador"]) or empty array if no roles
   - `memoryEnabled` (boolean): effective memory setting transported from the source that provides it (toggle UI or BD field, precedence defined in spec memoria-feedback-correcciones)

5. WHERE the user specifies an agent explicitly, THE Request_Payload SHALL include the field `agentType` with the specified agent identifier

6. WHERE the user specifies an invalid or unrecognized agent name, THE Request_Payload SHALL set `agentType` to "auto" for automatic agent selection by N8n_Orchestrator

7. WHERE the user does not specify an agent explicitly, THE Request_Payload SHALL include the field `agentType` with value "auto" for automatic agent selection by N8n_Orchestrator

8. THE N8n_Orchestrator SHALL classify user intention and route automatically to the correct agent (e.g., "Necesito un plan de comunicación" → trigger-comunicaciones) without requiring explicit agent specification

9. THE agente rag-mails SHALL be the ONLY exception to proactive routing: it SHALL activate only when the user explicitly queries about historical mail communications, and SHALL NOT be suggested or routed proactively by intention classification

10. THE Request_Payload SHALL NOT include sensitive data such as passwords, SECRET_KEY, or API keys

### Requirement 2: Definir estructura de Response_Payload

**User Story:** Como Django_Frontend, necesito recibir una respuesta estructurada del N8n_Orchestrator con contenido HTML renderizado y metadata de ejecución, para mostrar la respuesta al usuario y registrar información de trazabilidad.

#### Acceptance Criteria

1. THE Response_Payload SHALL include the field `output` as a string containing the agent's response

2. THE Response_Payload SHALL include the field `html_render` as a boolean indicating whether `output` contains HTML (true) or plain text (false)

3. FOR ALL responses in MVP 1, THE Response_Payload SHALL set `html_render` to true (HTML sanitizado es el único formato soportado en MVP 1)

4. THE Response_Payload SHALL include the field `metadata` as an object containing:
   - `agent_used` (string): identifier of the agent that processed the request ("rag-mails", "trigger-comunicaciones", "unknown")
   - `execution_time_ms` (number): execution time in milliseconds
   - `records_found` (number or null): number of records returned by agent (null if not applicable)

5. IF the N8n_Orchestrator encounters an error during execution, THEN THE Response_Payload SHALL include the field `error` as a string describing the error, AND SHALL set `output` to a user-friendly error message

6. THE Response_Payload SHALL include the field `conversationId` matching the value from Request_Payload

### Requirement 3: Validar campos requeridos de Request_Payload

**User Story:** Como N8n_Orchestrator, necesito validar que el Request_Payload recibido desde Django_Frontend contiene todos los campos requeridos con tipos de datos correctos, para rechazar payloads malformados antes de derivar a agentes.

#### Acceptance Criteria

1. WHEN N8n_Orchestrator receives a Request_Payload, THE N8n_Orchestrator SHALL validate that field `conversationId` exists and is a non-empty string

2. WHEN N8n_Orchestrator receives a Request_Payload, THE N8n_Orchestrator SHALL validate that field `query` exists and is a non-empty string

3. WHEN N8n_Orchestrator receives a Request_Payload, THE N8n_Orchestrator SHALL validate that field `user` exists and is an object

4. WHEN N8n_Orchestrator receives a Request_Payload, THE N8n_Orchestrator SHALL validate that `user.userId` exists and is a number

5. WHEN N8n_Orchestrator receives a Request_Payload, THE N8n_Orchestrator SHALL validate that `user.userEmail` exists and is a non-empty string

6. WHEN N8n_Orchestrator receives a Request_Payload, THE N8n_Orchestrator SHALL validate that `user.profile` exists and is one of the valid profile values: "Administrador", "Usuario IC", "Heavy user", "Macro", "Usuario"

7. WHEN N8n_Orchestrator receives a Request_Payload, THE N8n_Orchestrator SHALL validate that `user.roles` exists and is an array (empty array is valid)

8. WHERE `user.roles` is an array, THE N8n_Orchestrator SHALL validate that each element is a non-empty string

9. WHEN N8n_Orchestrator receives a Request_Payload, THE N8n_Orchestrator SHALL validate that `user.memoryEnabled` exists and is a boolean

10. IF any required field is missing or has incorrect type, THEN THE N8n_Orchestrator SHALL return HTTP 400 with Response_Payload containing `error` field describing the validation failure, regardless of whether the error description generation succeeds or fails

### Requirement 4: Generar ConversationId en Django_Frontend

**User Story:** Como Django_Frontend, necesito generar un ConversationId único al inicio de una nueva conversación y reutilizarlo en requests subsiguientes, para que el N8n_Orchestrator mantenga continuidad conversacional en memoria.

#### Acceptance Criteria

1. WHEN a new conversation starts, THE Django_Frontend SHALL generate a ConversationId with format `conv-<timestamp>-<random>` WHERE timestamp is Unix timestamp in base36 AND random is a 6-character alphanumeric string using characters [a-z0-9]

2. THE Django_Frontend SHALL store the generated ConversationId in Django session (server-side) using `request.session['conversationId']`

3. WHEN the Django_Frontend sends a subsequent request in the same conversation, THE Django_Frontend SHALL retrieve the ConversationId from `request.session['conversationId']` and include it in Request_Payload

4. WHEN the user explicitly starts a new conversation (e.g., clicking "Nueva conversación"), THE Django_Frontend SHALL generate a new ConversationId, replace the stored value in `request.session['conversationId']`, and use the new value in subsequent requests

5. WHEN `request.session` does not contain a ConversationId (first request in session), THE Django_Frontend SHALL generate a new ConversationId and store it in `request.session['conversationId']` before sending the first request

### Requirement 5: Enviar Request_Payload al webhook de n8n

**User Story:** Como Django_Frontend, necesito enviar el Request_Payload al N8n_Orchestrator mediante HTTP POST al webhook configurado, para que el orquestador procese la solicitud del usuario.

#### Acceptance Criteria

1. THE Django_Frontend SHALL send Request_Payload to the URL defined in environment variable `N8N_WEBHOOK_URL` using HTTP POST method

2. THE Django_Frontend SHALL set HTTP header `Content-Type: application/json` when sending Request_Payload

3. THE Django_Frontend SHALL serialize Request_Payload as valid JSON before sending

4. WHEN the user submits a query, THE Django_Frontend SHALL construct Request_Payload including all required fields from Requirement 1 before making the HTTP request

5. THE Django_Frontend SHALL include the current user's data from Django session context in the `user` object of Request_Payload

### Requirement 6: Recibir y procesar Response_Payload

**User Story:** Como Django_Frontend, necesito recibir el Response_Payload desde N8n_Orchestrator, validar su estructura y renderizar el contenido HTML al usuario, para completar el flujo conversacional.

#### Acceptance Criteria

1. WHEN the N8n_Orchestrator returns HTTP 200, THE Django_Frontend SHALL parse the response body as JSON

2. WHEN the N8n_Orchestrator returns HTTP 200 with empty body, THE Django_Frontend SHALL display error message "n8n respondió 200 pero con body vacío"

3. WHEN the N8n_Orchestrator returns HTTP 200 with non-JSON body, THE Django_Frontend SHALL display error message "La respuesta no es JSON: <body>"

4. WHEN the parsed Response_Payload contains field `html_render` with value true, THE Django_Frontend SHALL render the `output` field as sanitized HTML using the existing `renderAssistantContent()` function

5. WHEN the parsed Response_Payload contains field `html_render` with value false, THE Django_Frontend SHALL render the `output` field as plain text (not implemented in MVP 1, included for future compatibility)

6. WHEN the Response_Payload contains field `metadata`, THE Django_Frontend SHALL log the metadata values to browser console for debugging and future trazabilidad integration

### Requirement 7: Manejar errores de comunicación con N8n_Orchestrator

**User Story:** Como Django_Frontend, necesito manejar errores de conexión, timeouts y respuestas inválidas del N8n_Orchestrator, para informar al usuario de forma clara cuando el sistema no puede procesar su solicitud.

#### Acceptance Criteria

1. IF the N8n_Orchestrator returns HTTP status code other than 200, THEN THE Django_Frontend SHALL display error message "Error conectando con n8n: HTTP <status_code> - <response_body>"

2. IF the network request to N8n_Orchestrator fails due to connection error or timeout, THEN THE Django_Frontend SHALL display error message "Error conectando con n8n: <error_description>"

3. WHEN displaying an error message, THE Django_Frontend SHALL render the error as an assistant message in the conversation UI

4. WHEN displaying an error message, THE Django_Frontend SHALL remove the typing indicator before showing the error

5. WHEN an error occurs, THE Django_Frontend SHALL save the error message to the conversation history in localStorage so it persists across page reloads

6. THE Django_Frontend SHALL set a timeout of 30 seconds for requests to N8n_Orchestrator to prevent indefinite waiting

### Requirement 8: Construir User_Object desde contexto Django

**User Story:** Como Django_Frontend, necesito construir el User_Object a partir del usuario autenticado en sesión Django, para incluir datos correctos de perfil, roles y configuración de memoria en cada Request_Payload.

#### Acceptance Criteria

1. WHEN constructing User_Object, THE Django_Frontend SHALL retrieve `user.id` from Django session and assign it to `userId` as a number

2. WHEN constructing User_Object, THE Django_Frontend SHALL retrieve `user.email` from Django session and assign it to `userEmail` as a string

3. WHEN constructing User_Object, THE Django_Frontend SHALL concatenate `user.first_name` and `user.last_name` with a space between them and assign the result to `userName` as a string

4. WHERE `user.first_name` is empty or null, THE Django_Frontend SHALL use `user.username` as fallback value for `userName`

5. WHEN constructing User_Object, THE Django_Frontend SHALL retrieve `user.perfil` from Django session and assign it to `profile` as a string

6. WHEN constructing User_Object, THE Django_Frontend SHALL retrieve `user.roles` from Django session and convert it to an array of strings for the `roles` field

7. WHERE `user.perfil` is not "Usuario IC", THE Django_Frontend SHALL set `roles` to an empty array regardless of database value (per usuarios-demo-perfiles-permisos Requirement 4)

8. WHEN constructing User_Object, THE Django_Frontend SHALL retrieve the effective memory setting and assign it to `memoryEnabled` as a boolean (source of effective value is defined in spec memoria-feedback-correcciones, NOT in this spec)

### Requirement 9: Documentar dependencia con spec memoria-feedback-correcciones

**User Story:** Como desarrollador, necesito entender que este spec NO define la regla de precedencia entre toggle UI y campo BD para memoria, para evitar duplicar lógica de negocio entre specs.

#### Acceptance Criteria

1. THE Request_Payload SHALL transport the `memoryEnabled` value received from the source that provides it, without defining the precedence rule between toggle UI and BD field

2. THE spec `memoria-feedback-correcciones` SHALL define whether toggle UI or BD field `memoria_habilitada` has precedence when constructing the `memoryEnabled` value

3. THE Django_Frontend SHALL obtain the effective `memoryEnabled` value from the component or service defined in spec `memoria-feedback-correcciones` before constructing Request_Payload

4. THIS spec SHALL NOT include acceptance criteria that define the business logic for memory precedence (toggle vs BD)

### Requirement 10: Registrar limitación de MVP 1 para html_render

**User Story:** Como desarrollador, necesito documentar que MVP 1 solo soporta respuestas HTML con `html_render=true`, para que quede claro que soporte de plain text o Markdown es una evolución futura.

#### Acceptance Criteria

1. THE Response_Payload field `html_render` SHALL always be true in MVP 1 (HTML sanitizado es el único formato de respuesta soportado)

2. THE Django_Frontend SHALL implement rendering logic ONLY for `html_render=true` using the existing `renderAssistantContent()` function from `cs-chat-rag/js/api.js`

3. THE Response_Payload structure SHALL include the `html_render` field to maintain forward compatibility with future MVP versions that may support plain text or Markdown

4. THIS limitation SHALL be documented in spec `documentacion-local-y-limites-mvp` as a known constraint of MVP 1

## Conflicts and Decisions

### Conflict 1: USERNAME_FIELD es email (RESUELTO - Opción A con aclaración)

**Conflicto detectado:** En este proyecto el USERNAME_FIELD del modelo User es el email (definido en spec usuarios-demo-perfiles-permisos). No existe un campo "username" separado del email.

**Resolución aprobada:**

- `userId`: number (Django user.id, identificador numérico para trazabilidad)
- `userEmail`: string (user.email, que es el USERNAME_FIELD, identificador de autenticación)
- `userName`: string (user.first_name + " " + user.last_name, solo para display)

**Impacto:** User_Object contiene tres campos de identificación con propósitos diferentes.

**Documentación:** Requirement 1 AC4, Requirement 8 AC1-4

---

### Conflict 2: Validación estricta del schema de entrada (RESUELTO - Opción A)

**Conflicto detectado:** ¿Django debe validar el schema completo antes de enviar a n8n, o delegar validación a n8n?

**Resolución aprobada:** Django debe validar el schema completo antes de enviar a n8n. Si falta un campo requerido o el tipo es incorrecto, Django debe fallar antes del POST.

**Impacto:** Django_Frontend valida estructura de Request_Payload antes de hacer HTTP POST. N8n_Orchestrator también valida (defensa en profundidad).

**Documentación:** Requirement 3, Requirement 5 AC4

---

### Conflict 3: Transporte de memoria efectiva (RESUELTO - Opción A con aclaración de dependencia)

**Conflicto detectado:** ¿El contrato debe definir la regla de precedencia toggle-UI-vs-BD para memoria?

**Resolución aprobada:** El contrato transporta el valor efectivo de memoria que reciba. NO define la regla de precedencia. Ese comportamiento lo decide el spec `memoria-feedback-correcciones`.

**Impacto:** Request_Payload incluye campo `memoryEnabled` (boolean), pero la lógica de negocio para calcularlo vive en otro spec.

**Documentación:** Requirement 1 AC4 (campo memoryEnabled), Requirement 8 AC8, Requirement 9 (dependencia explícita)

---

### Conflict 4: Contrato unificado para todos los agentes (RESUELTO - Opción A)

**Conflicto detectado:** ¿Un contrato único para todos los agentes o contratos separados por agente?

**Resolución aprobada:** Un solo contrato de entrada para todos los agentes (RAG, Trigger Comunicaciones, futuros). N8n usa el campo `agentType` o la intención detectada para rutear.

**Impacto:** Request_Payload incluye campo opcional `agentType`. No se crean múltiples webhooks.

**Documentación:** Requirement 1 AC5-6, Glossary (Agent_Type)

---

### Conflict 5: html_render=true permanente en MVP 1 (RESUELTO - Opción A con limitación explícita)

**Conflicto detectado:** ¿MVP 1 debe soportar respuestas en plain text además de HTML?

**Resolución aprobada:** MVP 1 siempre devuelve HTML renderizado (`html_render=true`). Registrar como limitación explícita de MVP 1, no como diseño permanente. Respuestas futuras podrían soportar Markdown u otros formatos.

**Impacto:** Response_Payload incluye campo `html_render` (boolean), pero en MVP 1 siempre es `true`.

**Documentación:** Requirement 2 AC2-3, Requirement 6 AC4-5, Requirement 10 (limitación de MVP 1)

---

### Conflict 6: Estructura del objeto user en el payload (RESUELTO - Opción A)

**Conflicto detectado:** ¿El payload incluye objeto `user` completo o solo userId para resolver en n8n?

**Resolución aprobada:** El payload incluye un objeto `user` completo con userId, userEmail, userName, profile, roles, memoryEnabled. Django resuelve todos los datos del usuario antes de enviar.

**Impacto:** N8n recibe contexto completo del usuario, no necesita consultar BD de Django.

**Documentación:** Requirement 1 AC4, Requirement 8 (construcción de User_Object)

## Notes

### Dependencias de specs

- **usuarios-demo-perfiles-permisos**: Este spec asume que el modelo User ya existe con campos `id`, `email`, `first_name`, `last_name`, `perfil`, `roles`, `memoria_habilitada`
- **memoria-feedback-correcciones**: Ese spec define la regla de precedencia toggle-UI vs BD para el campo `memoryEnabled`
- **base-django-login-home**: Ese spec implementa autenticación y expone `request.user` al contexto de templates

### Estructura de ejemplo completa

**Request_Payload (ejemplo):**

```json
{
  "conversationId": "conv-1a2b3c4d-5e6f7g",
  "query": "¿Qué comunicaciones recientes hay sobre beneficios?",
  "timestamp": "2026-04-17T14:32:15.123Z",
  "user": {
    "userId": 42,
    "userEmail": "comustock.ci@gmail.com",
    "userName": "Luciano Zurlo",
    "profile": "Administrador",
    "roles": ["Diseñador", "Desarrollador"],
    "memoryEnabled": true
  },
  "agentType": "auto"
}
```

**Response_Payload (ejemplo):**

```json
{
  "conversationId": "conv-1a2b3c4d-5e6f7g",
  "output": "<p>Encontré 3 comunicaciones recientes sobre beneficios...</p>",
  "html_render": true,
  "metadata": {
    "agent_used": "rag-mails",
    "execution_time_ms": 450,
    "records_found": 3
  }
}
```

### Compatibilidad con cs-chat-rag

El contrato extiende el contrato heredado de ComuStock (`cs-chat-rag`) agregando campos nuevos:

- `user.userId` (nuevo: identificador numérico Django user.id, reemplaza "benja" como identificador)
- `user.userEmail` (nuevo: identificador de autenticación USERNAME_FIELD, reemplaza "benja" como identificador)
- `user.userName` (nuevo: solo display para UI, NO es identificador; first_name + last_name)
- `user.profile` (nuevo)
- `user.roles` (nuevo)
- `user.memoryEnabled` (nuevo)
- `timestamp` (nuevo)
- `agentType` (nuevo)
- `metadata` en respuesta (nuevo)

**Nota sobre identificadores**: El "benja" heredado era un identificador string hardcodeado. En Personal Stock se reemplaza por dos identificadores reales: `userEmail` (USERNAME_FIELD, autenticación) y `userId` (user.id numérico, trazabilidad). El campo `userName` NO es identificador, es solo display para UI.

Los campos originales de ComuStock se mantienen:

- `conversationId` (mismo nombre, misma función)
- `query` (mismo nombre, misma función)
- `output` en respuesta (mismo nombre, misma función)
- `html_render` en respuesta (mismo nombre, misma función)

### Validación de estructura

Django debe validar antes de enviar (Requirement 3). N8n debe validar al recibir (defensa en profundidad). Los agentes específicos validan sus propios contratos internos (definidos en specs `rag-mails-dataset-permissions` y `trigger-comunicaciones-email`).

### Información contextual

- Dataset histórico: `mails/output/relevamiento_enriquecido.json` con estructura en `ESTRUCTURA_DATASET.md`
- Sistema de permisos: 5 perfiles definidos en `usuarios-demo-perfiles-permisos`
- Brand key y tono: `brand_key_voz_tono_personal.md`
- Variable de entorno: `N8N_WEBHOOK_URL` definida en `.env.example`
- Trazabilidad obligatoria: `security-permissions.md` (registro completo implementado en spec `acciones-trazabilidad-metricas`)

### Mock de n8n (fuera de alcance)

Este spec NO define el comportamiento del mock de n8n cuando n8n no está disponible. El mock se implementa en otro spec (probablemente `base-django-login-home` o `documentacion-local-y-limites-mvp`) respetando el contrato definido aquí.
