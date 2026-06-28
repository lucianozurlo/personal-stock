# Devolución: Requirements - Spec 4 (acciones-trazabilidad-metricas)

**Fecha:** 2026-06-27
**Spec:** acciones-trazabilidad-metricas
**Fase:** requirements
**Veredicto:** ✅ COMPLETADO (con correcciones aplicadas)

---

## 1. Qué se generó

Se generó el documento `requirements.md` para el spec 4: acciones-trazabilidad-metricas, siguiendo el workflow Requirements-First con formato EARS estricto.

### Archivos creados

- `.kiro/specs/acciones-trazabilidad-metricas/.config.kiro`
- `.kiro/specs/acciones-trazabilidad-metricas/requirements.md`

### Estructura del documento

1. **Introduction**: Contexto del sistema de trazabilidad obligatoria según brief sección 10 y security-permissions.md
2. **Glossary**: 9 términos clave
3. **10 Requirements** con 67 Acceptance Criteria totales en formato EARS
4. **6 Conflicts and Decisions** resueltos
5. **Notes**: Dependencias, estructura de modelos Django, ejemplos, integración con /api/chat/, consideraciones de performance

---

## 2. Requirements generados

### R1: Registrar trazabilidad de toda ejecución de agente (12 AC)

- Crear WorkflowRun con state="created" antes de llamar al agente
- Campos requeridos: user_id, timestamp, user_message, detected_intention, selected_agent, selection_reason, permissions_applied, agent_response, execution_time_ms, final_state, error_message

### R2: Soportar estados de ejecución (10 AC)

- 12 estados: created, running, needs_input, waiting_human, pending_approval, approved, rejected, blocked_by_permissions, blocked_by_compliance, failed, cancelled, completed
- Actualización de estado en cada fase del ciclo de vida
- state_history para registrar transiciones con timestamp

### R3: Registrar decisiones del sistema (8 AC)

- Campo system_decisions (JSON) con agent selection, permission checks, data sources
- Incluir decisiones de filtrado (records before/after filter para RAG)
- Registrar aprobaciones, rechazos y correcciones

### R4: Exponer acciones del usuario actual (6 AC)

- Endpoint `/api/actions/` para usuarios autenticados
- Solo devuelve acciones del usuario actual (filtro por user_id)
- Respuesta: user_message (truncado), detected_intention, selected_agent, final_state, timestamp, execution_time_ms
- Paginación: 20 acciones por página, orden descendente por timestamp

### R5: Exponer métricas para perfiles privilegiados (6 AC)

- Endpoint `/api/metrics/` solo para Administrador y Usuario IC
- HTTP 403 para otros perfiles
- Métricas agregadas: total executions, by agent, by state, avg execution time, error rate
- Query params opcionales: start_date, end_date
- Agregación eficiente con queries de BD (no cargar todo en memoria)

### R6: Página de acciones con listado básico (7 AC)

- Ruta `/actions/` con template Django simple
- Tabla/cards con acciones recientes
- Color coding: completed (verde), failed/blocked (rojo), pending/waiting (amarillo), running/needs_input (azul)
- Click en acción: detalle completo (full user_message, agent_response, system_decisions, permissions_applied, error_message)
- Paginación con controles previous/next
- Solo usuarios autenticados (redirect a login si no)

### R7: Registrar trazabilidad en cada llamada a /api/chat/ (6 AC)

- Integración automática en endpoint `/api/chat/`
- Crear WorkflowRun al inicio, actualizar con selección de agente, respuesta y estado final
- Registro de errores si el agente falla
- **Transacción separada SÍNCRONA** (NO async, NO Celery en MVP 1) para que fallo de trazabilidad no tire respuesta al usuario

### R8: Registrar métricas básicas (6 AC)

- Modelo MetricEvent: event_type, agent, timestamp, value, metadata
- Eventos: agent_execution (con execution_time_ms), agent_error, permission_blocked
- Tabla separada de WorkflowRun para retention policies independientes
- `/api/metrics/` agrega MetricEvent (no WorkflowRun) para performance

### R9: Incluir metadata de trazabilidad en Response_Payload (6 AC)

- Objeto `metadata` en Response_Payload conforme a spec home-chat-orchestrator-contract
- Campos: agent_used, execution_time_ms, records_found
- Poblado desde WorkflowRun después de que agente completa

### R10: Permitir consulta de trazabilidad por administradores (6 AC)

- Endpoint `/api/admin/actions/` solo para Administrador
- HTTP 403 para otros perfiles
- Query param opcional: user_id (si no se provee, devuelve acciones de todos)
- Formato igual a `/api/actions/` + campos adicionales: user_email, user_name, permissions_applied, system_decisions

---

## 3. Decisiones aplicadas

### Decisión 1: WorkflowRun con campos estructurados + JSON

**Contexto:** ¿Un modelo con muchos campos o múltiples tablas relacionadas?
**Resolución:** Modelo único con campos estructurados para datos clave + JSON/TextField para datos variables (system_decisions, state_history). Permite flexibilidad sin complejidad prematura.

### Decisión 2: Registro en transacción separada SÍNCRONA (MVP 1)

**Contexto:** ¿Registro síncrono o asíncrono?
**Resolución:** Transacción separada SÍNCRONA simple en MVP 1 (NO Celery, NO threads, NO async). La trazabilidad se escribe en el mismo request pero en transacción separada para que un fallo de trazabilidad no tire la respuesta al usuario. Cola de tareas (Celery, RQ) queda como evolución futura para MVP posterior.

### Decisión 3: Sin política de retención en MVP 1

**Contexto:** ¿Cuánto tiempo retener WorkflowRun y MetricEvent?
**Resolución:** Sin política de retención automática en MVP 1 (retención indefinida). Documentar como limitación en spec 9 (documentacion-local-y-limites-mvp). Tablas separadas permiten políticas diferentes en el futuro.

### Decisión 4: NO hay mock de n8n — errores se trazan como failed

**Contexto:** ¿Cómo se traza una ejecución cuando n8n falla?
**Resolución:** Según spec `home-chat-orchestrator-contract` (Conflict 4), NO hay mock de n8n en el proyecto. Cuando n8n falla, se devuelve error claro y se traza con `final_state="failed"` + `error_message`, igual que cualquier otro error. NO se necesita campo `is_simulated` en WorkflowRun.

### Decisión 5: Protección de datos sensibles por permisos de lectura

**Contexto:** ¿Los campos de trazabilidad pueden contener PII o datos restringidos?
**Resolución:** SÍ, pero protegidos por permisos de lectura: solo el usuario ve su trazabilidad (R4), solo Administrador ve trazabilidad de todos (R10). La trazabilidad NO reintroduce contenido bloqueado — registra la respuesta bloqueada ("no tengo permiso..."), NO el contenido restringido.

### Decisión 6: Página de acciones con template Django simple (MVP 1)

**Contexto:** ¿SPA con filtros avanzados o template simple?
**Resolución:** Template Django simple con tabla/cards y paginación básica en MVP 1. NO es SPA, NO tiene filtros complejos. Evolución futura puede migrar a SPA si se necesita búsqueda/filtrado avanzado.

---

## 4. Correcciones aplicadas (2026-06-27)

### Corrección 1: Requirement 9 — Eliminada referencia a localStorage

**Problema detectado:** El user story mencionaba "registrar datos en localStorage", contradiciendo el spec home-chat-orchestrator-contract donde se decidió que estado de sesión vive en request.session (server-side).
**Corrección aplicada:** Eliminada la frase "y registrar datos en localStorage" del user story de Requirement 9. La metadata ya queda registrada server-side en WorkflowRun.

### Corrección 2: Conflict 4 y campo is_simulated — Eliminado mock de n8n

**Problema detectado:** El Conflict 4 original y el campo `is_simulated` del modelo WorkflowRun contradecían el spec home-chat-orchestrator-contract (Conflict 4), donde se decidió que NO hay mock de n8n en el proyecto.
**Corrección aplicada:**

- Reformulado Conflict 4: "Manejo de errores de n8n (sin mock)"
- Eliminado campo `is_simulated` del modelo WorkflowRun en Notes
- Eliminado `"simulated": false` del ejemplo de system_decisions JSON
- Eliminada referencia a tech.md sobre "marcar simulado: true"
- Aclarado que errores de n8n se trazan con `final_state="failed"` + `error_message`, igual que cualquier otro error

### Corrección 3: Requirement 7 AC6 — Clarificada transacción separada SÍNCRONA

**Problema detectado:** El AC original decía "asynchronously or in a separate transaction", sin especificar que en MVP 1 es transacción separada SÍNCRONA simple (sin Celery, threads ni async).
**Corrección aplicada:**

- Reescrito AC6: "execute all database writes in a separate transaction (synchronous) to ensure traceability is persisted even if subsequent processing fails, while avoiding blocking the agent response to the user"
- Aclarado en Conflict 2 que en MVP 1 se usa transacción separada SÍNCRONA simple (NO Celery, NO threads, NO async)
- Cola de tareas queda documentada solo como evolución futura para MVP posterior

---

## 5. Validaciones

✅ **EARS compliance**: Todos los AC usan patrones EARS correctos (WHEN/THEN, WHERE, THE...SHALL)
✅ **Dependencias**: Documenta dependencia de spec 3 (home-chat-orchestrator-contract) y que specs 5, 6 y 8 dependen de este
✅ **Reglas de trazabilidad**: Cumple con security-permissions.md ("sin trazabilidad, tarea no completa")
✅ **Estados del brief**: Incluye los 12 estados de la sección 9 del brief
✅ **Campos requeridos**: Registra todos los datos del brief sección 10 (usuario, fecha, mensaje, intención, agente, permisos, decisiones, respuesta, errores)
✅ **Perfiles y permisos**: /api/metrics/ solo Admin/Usuario IC, /api/actions/ usuario actual, /api/admin/actions/ solo Admin
✅ **Consistencia con specs previos**: Corregidas las 3 inconsistencias detectadas con specs 2 y 3
✅ **Sin errores de formato**: getDiagnostics no reporta problemas

---

## 6. Próximos pasos

El requirements.md está listo y corregido. Esperando aprobación explícita del usuario antes de proceder a la fase de design.

Una vez aprobado:

1. Generar design.md (arquitectura técnica, modelos Django, endpoints, integración con /api/chat/)
2. Generar tasks.md (lista de tareas de implementación con subtareas)
3. Implementación tarea por tarea

---

## 7. Notas técnicas

### Modelos Django propuestos

**WorkflowRun** (sin campo is_simulated):

- Identificación: user (FK), conversation_id
- Timestamps: created_at, updated_at, execution_time_ms
- Input: user_message, detected_intention
- Agent selection: selected_agent, selection_reason
- Permissions: permissions_applied, system_decisions (JSON)
- Output: agent_response, error_message
- State: final_state (12 choices), state_history (JSON)

**MetricEvent**:

- event_type, agent, timestamp, value, metadata (JSON)

### Endpoints

- `POST /api/chat/` — Integración automática de trazabilidad (modificar spec 3)
- `GET /api/actions/` — Lista acciones del usuario actual (autenticado)
- `GET /api/metrics/` — Métricas agregadas (Admin/Usuario IC)
- `GET /api/admin/actions/` — Lista acciones de cualquier usuario (solo Admin)
- `GET /actions/` — Página web con listado visual (autenticado)

### Performance (MVP 1)

- <10k registros estimados con 100 usuarios demo y uso moderado
- Sin optimización prematura (manejable sin particionamiento ni archivado)
- Si en MVP posterior crece: particionamiento por fecha, índices en user_id + timestamp, política de retención

---

**Estado:** requirements.md completado y corregido — esperando aprobación para continuar con design.md
