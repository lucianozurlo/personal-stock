# Validación Tarea 11.3 — home-chat-orchestrator-contract

**Fecha**: 2026-06-25
**Spec**: home-chat-orchestrator-contract
**Tarea**: 11.3 — Modificar sendMessage para incluir CSRF token
**Validador**: Kiro (Task Orchestrator)
**Ejecutor**: Claude Code

---

## Resumen Ejecutivo

**Veredicto**: ✅ **COMPLETED**

La tarea 11.3 cumple completamente con todos los criterios de aceptación definidos en tasks.md. La función `showTypingAndReply` (que implementa `sendMessage`) en `templates/js/app.js` está correctamente configurada para:

1. Usar el endpoint Django `/api/chat/` (constante `CHAT_API_URL` definida en línea 63)
2. Incluir headers obligatorios: `Content-Type: application/json` y `X-CSRFToken`
3. Usar credentials `same-origin` para enviar session cookie
4. Serializar payload con `query` y `agentType` (default "auto")

---

## Criterios de Aceptación Validados

### Criterio 1: Modificar función sendMessage (showTypingAndReply) para usar fetch('/api/chat/')

**Estado**: ✅ Cumplido

**Evidencia**:

- Constante `CHAT_API_URL = '/api/chat/'` ya estaba definida (tarea 11.1) — línea 63 de app.js
- El fetch apunta a esa constante — línea 823 de app.js:

```javascript
const resp = await fetch(CHAT_API_URL, {
```

**Fuente**: `templates/js/app.js` línea 823

---

### Criterio 2: Headers: 'Content-Type': 'application/json'

**Estado**: ✅ Cumplido

**Evidencia**:

- Línea 826 de app.js:

```javascript
headers: {
  "Content-Type": "application/json",
```

**Fuente**: `templates/js/app.js` línea 826

---

### Criterio 3: Headers: 'X-CSRFToken': getCsrfToken()

**Estado**: ✅ Cumplido

**Evidencia**:

- Línea 827 de app.js:

```javascript
  "X-CSRFToken": getCsrfToken(),
```

- La función `getCsrfToken()` existía desde tarea 11.2 — línea 802 de app.js:

```javascript
function getCsrfToken() {
  const name = "csrftoken";
  const cookies = document.cookie.split(";");
```

**Fuente**: `templates/js/app.js` líneas 802-809, 827

---

### Criterio 4: Credentials: 'same-origin' para incluir session cookie

**Estado**: ✅ Cumplido

**Evidencia**:

- Línea 829 de app.js:

```javascript
credentials: "same-origin",
```

**Fuente**: `templates/js/app.js` línea 829

---

### Criterio 5: Body: JSON.stringify({ query, agentType })

**Estado**: ✅ Cumplido

**Evidencia**:

- Línea 830 de app.js:

```javascript
body: JSON.stringify({ query: userText, agentType: "auto" }),
```

- `agentType` está hardcodeado a "auto" porque no hay UI de selección de agente en MVP 1 (per requirements.md Requirement 1 AC7: "WHERE the user does not specify an agent explicitly, THE Request_Payload SHALL include the field `agentType` with value 'auto'")

**Fuente**: `templates/js/app.js` línea 830

---

## Verificación contra requirements.md

### Requirement 5: Enviar Request_Payload al webhook de n8n

**Relevancia**: La tarea 11.3 implementa el envío desde frontend a Django (que luego envía a n8n).

**Cumplimiento**:

- ✅ AC2: "THE Django_Frontend SHALL set HTTP header `Content-Type: application/json`" — cumplido (línea 826)
- ✅ AC3: "THE Django_Frontend SHALL serialize Request_Payload as valid JSON" — cumplido (línea 830)
- ✅ AC4: "THE Django_Frontend SHALL construct Request_Payload including all required fields" — cumplido (query y agentType presentes)
- ✅ Credenciales: `same-origin` asegura que session cookie se envíe (línea 829)

### Design - Frontend Request Format

**Relevancia**: La tarea 11.3 implementa el formato de request frontend → Django.

**Cumplimiento**:

- ✅ Endpoint: `/api/chat/` (constante CHAT_API_URL)
- ✅ Método: POST
- ✅ Headers: Content-Type y X-CSRFToken
- ✅ Credentials: same-origin
- ✅ Body: JSON con query y agentType

---

## Hallazgos

### 1. agentType hardcodeado a "auto" — CORRECTO

**Descripción**: El payload siempre envía `agentType: "auto"`, sin opción de selección manual.

**Análisis**: Esto es correcto porque:

1. No hay UI de selección de agente en MVP 1 (no es parte del alcance de este spec)
2. Requirements.md Requirement 1 AC7 establece: "WHERE the user does not specify an agent explicitly, THE Request_Payload SHALL include the field `agentType` with value 'auto'"
3. El orquestador n8n es responsable de clasificar intención y rutear automáticamente

**Veredicto**: ✅ No es un defecto, es el comportamiento esperado.

---

### 2. getCsrfToken() — implementado en tarea 11.2

**Descripción**: La función `getCsrfToken()` ya estaba implementada desde tarea 11.2 (línea 802).

**Análisis**: La tarea 11.3 correctamente la invoca en el header `X-CSRFToken`.

**Veredicto**: ✅ Dependencia resuelta correctamente.

---

### 3. CHAT_API_URL — definida en tarea 11.1

**Descripción**: La constante `CHAT_API_URL = '/api/chat/'` ya estaba definida desde tarea 11.1 (línea 63).

**Análisis**: La tarea 11.3 correctamente la usa en el fetch.

**Veredicto**: ✅ Dependencia resuelta correctamente.

---

## Archivos Modificados

| Archivo                 | Cambio                                 | Líneas  |
| ----------------------- | -------------------------------------- | ------- |
| templates/js/app.js     | fetch() con headers CSRF y credentials | 823-831 |
| (ya existía desde 11.1) | Constante CHAT_API_URL                 | 63      |
| (ya existía desde 11.2) | Función getCsrfToken()                 | 802-809 |

---

## Próximos Pasos

### Tareas Pendientes en home-chat-orchestrator-contract

Faltan 4 tareas para completar el spec:

- **11.4**: Manejar Response_Payload en frontend
- **11.5**: Implementar función displayError en app.js
- **12.1**: Preparar entorno de testing
- **12.2**: Ejecutar checklist de testing manual
- **12.3**: Verificar logs y trazabilidad
- **13.1**: Crear devolución final

---

## Decisiones y Recomendaciones

### Recomendación 1: Continuar con tarea 11.4

La tarea 11.3 está completa y verificada. El siguiente paso natural es implementar la tarea 11.4 (Manejar Response_Payload en frontend), que depende de 11.3.

**Acción sugerida**: Marcar tarea 11.3 como [x] en tasks.md y actualizar PROGRESO.md con tarea actual: 11.4.

---

### Recomendación 2: Validar testing manual antes de marcar spec completed

Las tareas 12.1-12.3 son críticas para validar el flujo end-to-end. No marcar el spec como completed sin ejecutar el checklist de testing manual.

**Acción sugerida**: Después de completar tareas 11.4 y 11.5 (frontend), ejecutar testing manual (tareas 12.x) antes de cerrar el spec.

---

## Conclusión

La tarea 11.3 cumple completamente con todos los criterios de aceptación y requirements.md. La implementación está lista para continuar con tarea 11.4.

**Estado del Spec**: 10 de 14 tareas principales completadas (71%).

**Próxima acción**: Implementar tarea 11.4 (Manejar Response_Payload en frontend) con Claude Code en sesión nueva.

---

_Validación completada por Kiro Task Orchestrator — 2026-06-25_
