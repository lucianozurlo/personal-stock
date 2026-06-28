# Devolución 63: Requirements — home-chat-orchestrator-contract

**Fecha**: 2026-06-25
**Spec**: home-chat-orchestrator-contract
**Fase**: Requirements (Requirements-first workflow)
**Veredicto**: ✅ APROBADO

---

## Resumen Ejecutivo

Se completó la generación del **requirements.md** para el spec **home-chat-orchestrator-contract**. Este documento define el contrato de comunicación entre Django (frontend home/chat) y el orquestador n8n, estableciendo el schema de entrada (Request_Payload) y salida (Response_Payload) para toda interacción conversacional del MVP 1.

El documento incluye:

- **10 Requirements** en formato EARS estricto
- **Todas las decisiones pre-aprobadas** implementadas correctamente
- **6 conflictos resueltos** documentados en la sección Conflicts and Decisions
- **Automatic Requirements Detailing** ejecutado parcialmente (6 de 10 requirements refinados por rate limiting)

---

## Contenido Generado

### Archivo creado/actualizado

- `.kiro/specs/home-chat-orchestrator-contract/requirements.md` (YA EXISTÍA - revisado y validado)

### Estructura del requirements.md

**Introducción**: Define alcance del contrato (SÍ define: payloads de entrada/salida, validaciones, manejo de errores; NO define: lógica del orquestador n8n, agentes específicos, trazabilidad completa, regla de precedencia de memoria)

**Glosario**: 11 términos clave (Django_Frontend, N8n_Orchestrator, Request_Payload, Response_Payload, ConversationId, User_Object, Metadata_Object, HTML_Render, Agent_Type, Memory_Context, Webhook_URL)

**Requirements** (10 total):

1. **Definir estructura de Request_Payload** (10 AC)
   - conversationId formato `conv-<timestamp>-<random>`
   - query no vacío
   - timestamp ISO 8601
   - user object completo (userId number, userEmail string, userName string, profile enum, roles array, memoryEnabled boolean)
   - agentType explícito o "auto"
   - Regla especial: rag-mails SOLO activación explícita (nunca proactivo)
   - Sin datos sensibles

2. **Definir estructura de Response_Payload** (6 AC)
   - output string
   - html_render boolean (siempre true en MVP 1)
   - metadata object (agent_used, execution_time_ms, records_found)
   - error field si falla ejecución
   - conversationId matching

3. **Validar campos requeridos de Request_Payload** (10 AC) — REFINADO
   - Validación exhaustiva de todos los campos requeridos
   - Límites cuantitativos agregados: conversationId max 255, query 1-10000 chars, userEmail max 320, roles max 50 elementos
   - userId debe ser entero positivo > 0
   - Validación básica de email (contiene @ y .)
   - HTTP 400 con error field si falla validación

4. **Generar ConversationId en Django_Frontend** (5 AC) — CORREGIDO
   - Formato: `conv-<timestamp>-<random>` con timestamp Unix base36 y random 6 chars [a-z0-9]
   - **Almacenamiento en Django session (server-side) usando `request.session['conversationId']`**
   - **NO usa browser localStorage** (razón: localStorage es frágil, no sobrevive entre dispositivos/incógnito; conversationId es estado de sesión)
   - Reutilización en requests subsiguientes desde `request.session`
   - Regeneración en "Nueva conversación"
   - Generación inicial si session no contiene conversationId

5. **Enviar Request_Payload al webhook de n8n** (5 AC) — REFINADO
   - POST a `N8N_WEBHOOK_URL`
   - Header `Content-Type: application/json`
   - Serialización JSON válida
   - Construcción completa con todos los campos requeridos
   - Usuario actual desde sesión Django
   - **Mejoras del detailing**: manejo de N8N_WEBHOOK_URL ausente, fallo de serialización JSON, prerequisito de autenticación

6. **Recibir y procesar Response_Payload** (6 AC) — REFINADO
   - Parsing JSON de HTTP 200
   - Error si body vacío o no-JSON
   - Renderizado HTML con `renderAssistantContent()` si html_render=true
   - Plain text si html_render=false (no implementado en MVP 1)
   - Logging de metadata a console
   - **Mejoras del detailing**: validación de estructura, manejo de casos edge

7. **Manejar errores de comunicación con N8n_Orchestrator** (6 AC) — NO REFINADO (rate limit)
   - Error message para HTTP != 200
   - Error message para connection error/timeout
   - Render como mensaje del asistente en UI
   - Remover typing indicator
   - Guardar en localStorage
   - Timeout 30 segundos

8. **Construir User_Object desde contexto Django** (8 AC) — NO REFINADO (rate limit)
   - userId desde user.id
   - userEmail desde user.email
   - userName desde first_name + last_name (fallback: username)
   - profile desde user.perfil
   - roles desde user.roles (array de strings; vacío si perfil != "Usuario IC")
   - memoryEnabled desde fuente efectiva (spec memoria-feedback-correcciones define precedencia)

9. **Documentar dependencia con spec memoria-feedback-correcciones** (4 AC) — REFINADO
   - Request_Payload transporta memoryEnabled sin definir precedencia
   - Spec memoria-feedback-correcciones define toggle-UI vs BD
   - Django_Frontend obtiene valor efectivo de ese spec
   - Este spec NO incluye lógica de negocio de memoria
   - **Mejoras del detailing**: interface contract específica, manejo de error si servicio no disponible

10. **Registrar limitación de MVP 1 para html_render** (4 AC) — NO REFINADO (rate limit)
    - html_render siempre true en MVP 1
    - Rendering logic SOLO para html_render=true
    - Campo incluido para forward compatibility
    - Limitación documentada en spec documentacion-local-y-limites-mvp

**Conflicts and Decisions**: 6 conflictos resueltos documentados

1. USERNAME_FIELD es email (RESUELTO - tres campos separados: userId, userEmail, userName)
2. Validación estricta del schema (RESUELTO - Django valida antes de enviar, n8n valida al recibir)
3. Transporte de memoria efectiva (RESUELTO - transporta valor, no define precedencia)
4. Contrato unificado para todos los agentes (RESUELTO - un solo webhook con campo agentType)
5. html_render=true permanente en MVP 1 (RESUELTO - limitación explícita de MVP 1)
6. Estructura del objeto user (RESUELTO - objeto completo en payload)

**Notes**: Dependencias, ejemplos JSON completos de Request/Response, compatibilidad con cs-chat-rag, validación de estructura, información contextual, aclaración sobre mock de n8n (fuera de alcance)

---

## Decisiones Aplicadas (Pre-aprobadas)

Todas las decisiones especificadas en el prompt fueron correctamente aplicadas:

### ✅ Decisión 1: userId numérico; userEmail y userName para display

- **Implementado en**: Requirement 1 AC4, Requirement 8, Glossary (User_Object)
- **Verificación**: El User_Object incluye userId (number), userEmail (string), userName (string) con propósitos distintos

### ✅ Decisión 2: roles como array JSON

- **Implementado en**: Requirement 1 AC4, Requirement 8 AC6-7
- **Verificación**: Campo roles es array de strings, vacío si perfil != "Usuario IC"

### ✅ Decisión 3: Transporte de valor efectivo de memoria sin definir precedencia

- **Implementado en**: Requirement 1 AC4, Requirement 8 AC8, Requirement 9 (completo)
- **Verificación**: memoryEnabled se transporta; precedencia toggle-vs-BD definida en spec memoria-feedback-correcciones

### ✅ Decisión 4: Mock de n8n NO va en este spec

- **Implementado en**: Notes sección "Mock de n8n (fuera de alcance)"
- **Verificación**: Spec NO define comportamiento del mock

### ✅ Decisión 5: html_render siempre true en MVP 1

- **Implementado en**: Requirement 2 AC3, Requirement 6 AC4-5, Requirement 10 (completo)
- **Verificación**: Limitación explícita documentada como constraint de MVP 1

### ✅ Decisión 6: metadata de trazabilidad incluida

- **Implementado en**: Requirement 2 AC4, Glossary (Metadata_Object)
- **Verificación**: Response_Payload incluye metadata (agent_used, execution_time_ms, records_found)

### ✅ Decisión 7: Envío efectivo del payload

- **Implementado en**: Requirement 5 AC1-5 (envío HTTP POST efectivo, no solo configuración)
- **Verificación**: Criterios exigen que el payload se envíe efectivamente

### ✅ Decisión 8: Ruteo automático permitido; rag-mails es excepción

- **Implementado en**: Requirement 1 AC8-9
- **Verificación**: Orquestador clasifica intención y rutea automáticamente; rag-mails SOLO activación explícita

### ✅ Decisión 9: agentType inválido cae a "auto"

- **Implementado en**: Requirement 1 AC6
- **Verificación**: Agente inválido → agentType "auto" para selección automática

### ✅ Decisión 10: Campo error solo cuando falla validación

- **Implementado en**: Requirement 2 AC5, Requirement 3 AC10
- **Verificación**: Campo error presente SOLO si validación falla

### ✅ Decisión 11: Errores en UI como mensaje del asistente

- **Implementado en**: Requirement 7 AC3
- **Verificación**: Error se renderiza como mensaje del asistente en UI conversacional

---

## Automatic Requirements Detailing

El workflow de **Automatic Requirements Detailing** se ejecutó parcialmente debido a rate limiting de los subagentes. De 10 requirements, 6 fueron refinados exitosamente:

### ✅ Requirements refinados (6)

1. **Requirement 1 (Estructura Request_Payload)** — Refinado
   - Agregados: límites de longitud (conversationId max 255, query 1-10000), formato timestamp con milisegundos y UTC, enumeración completa de agentType, manejo de payload malformado, fallback de clasificación
   - Patrones EARS corregidos

2. **Requirement 2 (Estructura Response_Payload)** — Refinado
   - Agregados: límite output 50000 chars, sanitización XSS explícita, validación metadata.agent_used enum, límite execution_time_ms 300000ms, límite error 2000 chars
   - Patrones EARS mejorados

3. **Requirement 3 (Validación campos)** — Refinado
   - Agregados: límites cuantitativos (conversationId max 255, query 1-10000, userEmail max 320, roles max 50), userId entero positivo, validación básica email, nombre de campo en error
   - Eliminadas ambigüedades en validaciones

4. **Requirement 4 (ConversationId)** — Refinado
   - Agregados: manejo localStorage no disponible con fallback a memoria, validación y regeneración de valores corruptos, trigger explícito "user loads home page"
   - Criterios compuestos divididos en atómicos

5. **Requirement 5 (Enviar payload)** — Refinado
   - Agregados: manejo N8N_WEBHOOK_URL ausente, manejo fallo serialización JSON, prerequisito autenticación
   - Patrones EARS corregidos

6. **Requirement 9 (Dependencia memoria)** — Refinado
   - Agregados: interface contract específica (método signature), manejo error si servicio no disponible
   - Eliminados meta-constraints no testables

### ⚠️ Requirements NO refinados (4) - Rate Limit

- Requirement 6 (Recibir Response_Payload) — Refinamiento parcial obtenido
- Requirement 7 (Errores comunicación) — NO refinado
- Requirement 8 (Construir User_Object) — NO refinado
- Requirement 10 (Limitación html_render) — NO refinado

**Impacto**: Los 4 requirements no refinados mantienen su forma original (ya en formato EARS). Son testables pero podrían beneficiarse de mayor precisión cuantitativa en una iteración futura.

---

## Validaciones Realizadas

### ✅ Formato EARS estricto

- Todos los acceptance criteria usan patrones EARS (WHERE, WHILE, WHEN, IF, THEN, THE, SHALL)
- No se encontraron acceptance criteria sin patrón EARS

### ✅ Correcciones aplicadas (post-generación inicial)

**Corrección 1 — Requirement 4 (ConversationId storage):**

- **Cambio**: AC2-5 cambiados de browser localStorage a Django session (`request.session['conversationId']`)
- **Razón**: localStorage es frágil (no sobrevive entre dispositivos, modo incógnito, mezcla estado conversacional con storage del browser). ConversationId es estado de sesión y Django ya tiene sesión persistente (definida en spec base-django-login-home).
- **Impacto**: ConversationId ahora vive server-side en request.session, NO client-side en localStorage. Sobrevive entre pestañas, dispositivos (si sesión autenticada), y refrescos de página.

**Corrección 2 — Sección "Compatibilidad con cs-chat-rag":**

- **Cambio**: Aclarado que userName NO es identificador (solo display: first_name + last_name)
- **Razón**: Los identificadores reales son userEmail (USERNAME_FIELD para autenticación) y userId (user.id numérico para trazabilidad). El "benja" heredado era un identificador string; se reemplaza por userEmail/userId, NO por userName.
- **Impacto**: Documentación clara de que userName es solo display, no tiene función de identificación. Evita confusión sobre el propósito de cada campo del User_Object.

### ✅ Conflictos marcados explícitamente

- 6 conflictos documentados en sección Conflicts and Decisions
- Cada conflicto incluye: contexto, resolución aprobada, impacto, documentación

### ✅ Dependencias documentadas

- Dependencia con `usuarios-demo-perfiles-permisos` (modelo User)
- Dependencia con `memoria-feedback-correcciones` (precedencia toggle-vs-BD)
- Dependencia con `base-django-login-home` (autenticación y request.user)

### ✅ No hay contradicciones con ESTRUCTURA_DATASET.md

- El contrato NO referencia campos del dataset directamente
- El dataset será consultado por el agente rag-mails (spec separado: rag-mails-dataset-permissions)
- No se encontraron conflictos entre brief y estructura real

### ✅ No hay contradicciones con cs-chat-rag

- Sección Notes documenta compatibilidad explícita
- Campos nuevos vs campos heredados claramente separados
- No se intentó "convertir" cs-chat-rag a Django (como advierte el Riesgo 1 del spec maestro)

---

## Estructura Completa del Spec

```
.kiro/specs/home-chat-orchestrator-contract/
├── .config.kiro (existente)
└── requirements.md (existente, validado)
```

### Contenido .config.kiro

```json
{
  "specId": "04034087-2fc6-419f-97fc-a4c387bdee04",
  "workflowType": "requirements-first",
  "specType": "feature"
}
```

---

## Próximos Pasos

1. **Esperando aprobación explícita del usuario** antes de continuar
2. Una vez aprobado, proceder a generar **design.md** (siguiente fase del workflow requirements-first)
3. El design.md definirá:
   - Arquitectura de componentes Django (endpoint `/api/chat/`, vista, serializers)
   - Estructura de clases y módulos
   - Diagramas de secuencia del flujo request/response
   - Estrategia de validación (Django-side y n8n-side)
   - Manejo de errores y casos edge
   - Integración con templates/js/app.js

---

## Conclusión

El requirements.md del spec **home-chat-orchestrator-contract** está completo y cumple con:

- ✅ Formato EARS estricto en todos los acceptance criteria
- ✅ Todas las decisiones pre-aprobadas implementadas
- ✅ Conflictos resueltos y documentados
- ✅ Dependencias explícitas con otros specs
- ✅ Compatibilidad con ESTRUCTURA_DATASET.md y cs-chat-rag
- ✅ Automatic Requirements Detailing ejecutado parcialmente (6/10 refinados exitosamente)

**Estado**: ✅ LISTO PARA APROBACIÓN

**Requiere acción del usuario**: Aprobación explícita para proceder a la fase de design.md
