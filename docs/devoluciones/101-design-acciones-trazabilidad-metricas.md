# Devolución: Design - Spec 4 (acciones-trazabilidad-metricas)

**Fecha:** 2026-06-27
**Spec:** acciones-trazabilidad-metricas
**Fase:** design
**Veredicto:** ✅ COMPLETADO

---

## 1. Qué se generó

Se generó el documento `design.md` para el spec 4: acciones-trazabilidad-metricas, detallando la arquitectura técnica completa del sistema de trazabilidad y métricas obligatorio.

### Archivo creado

- `.kiro/specs/acciones-trazabilidad-metricas/design.md`

### Estructura del documento

1. **Overview**: Visión general del sistema con 2 modelos principales (WorkflowRun, MetricEvent)
2. **Architecture**: Diagramas de interacción de componentes y arquitectura en capas
3. **Components and Interfaces**: 3 service classes + 4 endpoints REST detallados
4. **Data Models**: Estructura completa de WorkflowRun y MetricEvent con índices
5. **Testing Strategy**: 25+ test cases (unit, integration, template) — NO PBT
6. **Error Handling**: 5 categorías de errores con estrategias de manejo
7. **Implementation Notes**: Integración con chat_view, transacciones, permisos, métricas
8. **Security Considerations**: 5 vectores de ataque con mitigaciones
9. **Performance Optimization**: Índices, queries, caching, volumen de datos
10. **Deployment Considerations**: Variables de entorno, setup de BD, monitoring
11. **Dependencies**: Specs dependientes, Python packages, frontend files
12. **Migration Path**: 7 pasos desde estado actual a implementación completa
13. **Open Questions and Future Work**: 3 preguntas para implementación, 7 items de MVP 2+

---

## 2. Arquitectura diseñada

### 2.1 Componentes principales

**Service Classes**:

1. **TraceabilityManager**: CRUD de WorkflowRun con transacciones separadas síncronas
   - `create_run()`: Crea WorkflowRun con state="created"
   - `update_run_agent_selection()`: Transición created → running
   - `complete_run()`: Transición running → completed
   - `fail_run()`: Marca como failed con error_message

2. **MetricsAggregator**: Genera métricas agregadas usando Django ORM
   - `get_summary_metrics()`: Total executions, by agent, by state, avg time, error rate
   - `record_metric_event()`: Crea MetricEvent para agregación futura

3. **PermissionChecker**: Control de acceso por perfil
   - `can_access_metrics()`: Solo Admin/Usuario IC
   - `can_access_admin_actions()`: Solo Admin
   - `get_user_runs_queryset()`: Filtra por usuario
   - `get_all_runs_queryset()`: Admin ve todas (con filtro opcional por user_id)

### 2.2 Modelos Django

**WorkflowRun** (trazabilidad completa):

- **Identificación**: user (FK), conversation_id
- **Timestamps**: created_at, updated_at, execution_time_ms
- **Input**: user_message, detected_intention
- **Agent selection**: selected_agent, selection_reason
- **Permissions**: permissions_applied, system_decisions (JSON)
- **Output**: agent_response, error_message
- **State**: final_state (12 choices), state_history (JSON list)
- **Índices**: `(user, -created_at)`, `final_state`, `selected_agent`, `created_at`

**MetricEvent** (agregación):

- event_type, agent, timestamp, value, metadata (JSON)
- **Índices**: `(event_type, timestamp)`, `(agent, timestamp)`

### 2.3 Endpoints REST

| Endpoint              | Method | Auth     | Permisos         | Paginación | Response                      |
| --------------------- | ------ | -------- | ---------------- | ---------- | ----------------------------- |
| `/api/actions/`       | GET    | Required | Todos            | 20 items   | Acciones del usuario actual   |
| `/api/metrics/`       | GET    | Required | Admin/Usuario IC | N/A        | Métricas agregadas            |
| `/api/admin/actions/` | GET    | Required | Solo Admin       | 20 items   | Acciones de cualquier usuario |
| `/actions/`           | GET    | Required | Todos            | 20 items   | Página web con listado visual |

### 2.4 Integración con /api/chat/

**Flujo de trazabilidad** (modificaciones en `core/views.py::chat_view()`):

```python
1. Parsear request body y validar
2. TraceabilityManager.create_run() → WorkflowRun(state="created")
3. Llamar n8n orchestrator
4a. Si éxito: TraceabilityManager.complete_run() → state="completed"
4b. Si error: TraceabilityManager.fail_run() → state="failed"
5. Incluir metadata en Response_Payload
6. Retornar respuesta al usuario
```

**Transacción separada síncrona**:

- Cada método de TraceabilityManager usa `transaction.atomic()`
- Commit inmediato, no espera al final del request
- Si trazabilidad falla, NO bloquea respuesta al usuario (log error, return None)

---

## 3. Decisiones técnicas aplicadas

### Decisión 1: WorkflowRun con campos estructurados + JSON

**Contexto:** ¿Un modelo con muchos campos o múltiples tablas relacionadas?
**Resolución:** Modelo único con campos estructurados para datos clave (user, timestamp, selected_agent, final_state) y JSON para datos variables (system_decisions, state_history).
**Razón:** Flexibilidad sin complejidad prematura. Si MVP posterior necesita queries dentro de JSON, se puede normalizar.

### Decisión 2: Transacción separada SÍNCRONA (no async, no Celery)

**Contexto:** ¿Registro síncrono o asíncrono?
**Resolución:** Transacción separada SÍNCRONA simple en MVP 1. Django `transaction.atomic()` con commit inmediato.
**Razón:** 100 usuarios demo + uso moderado no requieren Celery. Evita complejidad. Cola de tareas queda como evolución futura.

### Decisión 3: Sin política de retención en MVP 1

**Contexto:** ¿Cuánto tiempo retener WorkflowRun y MetricEvent?
**Resolución:** Retención indefinida en MVP 1. Documentar como limitación en spec 9.
**Estimación:** 15k registros (~30 MB) manejable sin optimización.
**Futuro:** Archivar registros > 90 días en MVP posterior.

### Decisión 4: Template Django simple (no SPA)

**Contexto:** ¿SPA con filtros avanzados o template simple?
**Resolución:** Template Django simple con tabla/cards y paginación básica. NO SPA.
**Razón:** Suficiente para MVP 1. Evolución a SPA en MVP posterior si se necesita búsqueda/filtrado avanzado.

### Decisión 5: NO usar Property-Based Testing

**Contexto:** ¿Es apropiado PBT para este feature?
**Resolución:** NO. Este feature consiste en side effects (escritura a BD), CRUD operations, integración con infraestructura.
**Razón:** No hay transformaciones de datos con propiedades universales. Usar unit tests + integration tests + template tests.

### Decisión 6: Errores de trazabilidad NO bloquean usuario

**Contexto:** ¿Qué pasa si falla crear/actualizar WorkflowRun?
**Resolución:** TraceabilityManager loggea error pero NO propaga excepción. Retorna None. chat_view continúa y responde al usuario.
**Impacto:** Gap en trazabilidad (registro perdido), pero usuario NO afectado.

### Decisión 7: Usar constantes User.Profile en lugar de strings literales

**Contexto:** PermissionChecker compara user.perfil con strings literales ('Administrador', 'Usuario IC'). Esto es frágil ante typos o cambios de naming.
**Resolución:** Usar las constantes de TextChoices del modelo User (spec 2: usuarios-demo-perfiles-permisos): `User.Profile.ADMINISTRADOR`, `User.Profile.USUARIO_IC`, etc.
**Razón:** Evita errores por typos, refactor-safe, autocompletado en IDEs, type checking con mypy/pyright.
**Impacto:** Todas las comparaciones de perfil en PermissionChecker, views de API, y tests deben usar estas constantes. Si el modelo User no las expone públicamente, deben agregarse explícitamente al spec 2.
**Ubicaciones afectadas:**

- `PermissionChecker.can_access_metrics()`: `user.perfil in [User.Profile.ADMINISTRADOR, User.Profile.USUARIO_IC]`
- `PermissionChecker.can_access_admin_actions()`: `user.perfil == User.Profile.ADMINISTRADOR`
- Views de API: Validación de permisos antes de procesar requests
- Tests: Assertions de perfil

---

## 4. Testing Strategy (25+ test cases)

### Unit Tests (6 casos)

- `test_create_run_sets_initial_state`: Verifica state="created" inicial
- `test_update_run_agent_selection_transitions_to_running`: Verifica transición created → running
- `test_complete_run_sets_final_state`: Verifica state="completed" al finalizar
- `test_fail_run_records_error_message`: Verifica state="failed" + error_message
- `test_metrics_aggregator_counts_executions_by_agent`: Verifica agregación por agente
- `test_metrics_aggregator_filters_by_date_range`: Verifica filtrado por fecha

### Integration Tests - API Endpoints (9 casos)

- `test_api_actions_returns_only_user_runs`: Filtra por usuario autenticado
- `test_api_actions_requires_authentication`: HTTP 401 sin autenticación
- `test_api_actions_paginates_results`: 20 items por página
- `test_api_metrics_requires_privileged_profile`: HTTP 403 para perfil Usuario
- `test_api_metrics_allows_administrador`: HTTP 200 para Admin
- `test_api_metrics_returns_aggregated_data`: Estructura correcta de métricas
- `test_api_admin_actions_requires_administrador`: HTTP 403 para no-Admin
- `test_api_admin_actions_returns_all_users_runs`: Admin ve acciones de todos
- `test_api_admin_actions_filters_by_user_id`: Filtro opcional por user_id

### Integration Tests - chat_view (6 casos)

- `test_chat_view_creates_workflow_run`: WorkflowRun creado al inicio
- `test_chat_view_updates_run_on_success`: Actualización con respuesta exitosa
- `test_chat_view_updates_run_on_failure`: Actualización con error de n8n
- `test_chat_view_records_execution_time`: execution_time_ms > 0
- `test_chat_view_includes_metadata_in_response`: metadata en Response_Payload
- `test_traceability_does_not_block_user_response`: Error de trazabilidad no bloquea usuario

### Model Tests (3 casos)

- `test_workflow_run_indexes_exist`: Verifica índices definidos
- `test_add_state_transition_updates_history`: Verifica state_history actualizado
- `test_metric_event_defaults`: Verifica defaults de MetricEvent

### Template Tests (4 casos)

- `test_actions_page_requires_login`: Redirect a /login/ sin autenticación
- `test_actions_page_renders_user_runs`: Renderiza action cards del usuario
- `test_actions_page_color_codes_states`: Clases CSS correctas por estado
- `test_actions_page_paginates`: Paginación con 20 items por página

**Test Coverage Goal**: >80% en service classes, 100% en endpoints de API.

---

## 5. Error Handling

### Categorías de errores diseñadas

**1. Traceability Errors (Non-Blocking)**:

- BD no disponible durante create_run() → Log error, return None, usuario NO afectado
- JSON serialization error en system_decisions → Convertir a string fallback, continuar
- Estado inválido en state transition → Log error, mantener estado anterior

**2. API Endpoint Errors (User-Facing)**:

- Usuario no autenticado → HTTP 401 (Django @login_required)
- Perfil sin permisos → HTTP 403 con mensaje claro
- Página de paginación inválida → HTTP 400/404
- Query date range inválido → HTTP 400

**3. n8n Integration Errors**:

- n8n timeout → WorkflowRun state="failed", HTTP 504
- n8n connection refused → WorkflowRun state="failed", HTTP 503
- n8n invalid JSON → WorkflowRun state="failed", HTTP 502

**4. Database Errors**:

- BD no disponible durante escritura → Si trazabilidad: no bloquear; si operación principal: HTTP 500
- Constraint violation → Truncar campo si posible
- Query timeout en métricas → HTTP 504 con mensaje sugerido

**5. Edge Cases**:

- Usuario sin runs → `{"count": 0, "results": []}`
- Filtro sin resultados → Métricas con valores en 0
- user_message extremadamente largo → Validar max 100k caracteres, HTTP 400
- system_decisions JSON inválido → Convertir a string fallback

---

## 6. Security Considerations

**1. Data Exposure**:

- Solo usuario ve su trazabilidad completa
- Administrador puede ver trazabilidad de todos
- No reintroduce contenido restringido (registra respuesta bloqueada, NO contenido bloqueado)

**2. SQL Injection**:

- Django ORM automáticamente sanitiza queries
- Nunca usar raw SQL con input de usuario sin parameterización

**3. XSS (Cross-Site Scripting)**:

- Django templates auto-escape por defecto
- `agent_response` ya sanitizado por HTMLSanitizer antes de guardarse

**4. CSRF**:

- Todos los endpoints POST usan `@csrf_protect`

**5. Authorization Bypass**:

- Todos los endpoints usan `@login_required`
- Permisos verificados con PermissionChecker
- Queryset filtrado por usuario antes de retornar datos

---

## 7. Performance Optimization

### Índices críticos definidos

**WorkflowRun**:

- `(user, -created_at)` → Para `/api/actions/` (filtra por user, ordena por fecha desc)
- `final_state` → Para métricas por estado
- `selected_agent` → Para métricas por agente
- `created_at` → Para filtrado por rango de fechas

**MetricEvent**:

- `(event_type, timestamp)` → Para métricas por tipo y fecha
- `(agent, timestamp)` → Para métricas por agente y fecha

**Impacto**: Con índices, queries en 10k registros < 50ms. Sin índices: > 500ms.

### Query Optimization

- **N+1 Query Prevention**: Usar `select_related('user')` en querysets de WorkflowRun
- **Aggregation SQL**: Django ORM aggregation (Count, Avg, annotate, values)
- **Pagination**: Django REST Framework limita resultados automáticamente

### Data Volume Management (MVP 1)

**Estimación**:

- 100 usuarios demo × 5 queries/día × 30 días = 15.000 registros
- Tamaño promedio: 2 KB/registro
- Total: ~30 MB

**Conclusión**: Volumen manejable sin optimización compleja en MVP 1.

**MVP posterior**: Archivado de registros > 90 días, compresión de JSON, particionamiento por fecha.

---

## 8. Deployment Considerations

### Environment Variables

- No se necesitan nuevas variables de entorno
- Usa configuración existente: `DATABASE_URL`, `DJANGO_SECRET_KEY`

### Database Setup

```bash
cd app
python manage.py makemigrations core
python manage.py migrate
python manage.py shell
>>> from core.models import WorkflowRun, MetricEvent
>>> WorkflowRun.objects.count()
0
```

### Initial Data

- No se necesitan fixtures
- WorkflowRun se crea automáticamente cuando usuarios usan `/api/chat/`

### Monitoring

**Logs críticos**:

- Errores de trazabilidad: `logger.error("Failed to create WorkflowRun")`
- Errores de permisos: `logger.warning("User without permissions tried to access /api/metrics/")`
- Performance: `logger.info("Metrics query took X ms")`

---

## 9. Dependencies

### Spec Dependencies

**Este spec depende de**:

1. `usuarios-demo-perfiles-permisos`: User model con campo `perfil`, roles
2. `home-chat-orchestrator-contract`: Contrato de `/api/chat/`, estructura de metadata
3. `base-django-login-home`: Autenticación, sesiones, templates base

**Specs que dependen de este**:

1. `rag-mails-dataset-permissions`: Debe registrar trazabilidad en cada consulta RAG
2. `trigger-comunicaciones-email`: Debe registrar trazabilidad en cada trigger
3. `memoria-feedback-correcciones`: Usará WorkflowRun para historial conversacional

### Python Dependencies

- Django >= 5.2 (ya instalado)
- djangorestframework (ya instalado)
- dj-database-url (ya instalado)
- **No se necesitan nuevas dependencias**

### Frontend Dependencies

**Archivos nuevos a crear**:

- `templates/actions.html`
- `templates/css/actions.css`
- `templates/js/actions.js`

---

## 10. Migration Path (7 pasos)

Desde estado actual (sin trazabilidad) a implementación completa:

1. **Crear modelos** (WorkflowRun, MetricEvent)
   - Run migrations
   - Verificar en Django admin

2. **Implementar TraceabilityManager**
   - Service class con métodos create_run, update_run, etc.
   - Tests unitarios

3. **Modificar chat_view**
   - Agregar llamadas a TraceabilityManager
   - Verificar que errores de trazabilidad no bloquean respuesta

4. **Implementar endpoints de API**
   - `/api/actions/`, `/api/metrics/`, `/api/admin/actions/`
   - Tests de integración

5. **Crear template actions.html**
   - HTML + CSS + JS
   - Verificar rendering

6. **Implementar MetricsAggregator**
   - Queries de agregación
   - Tests de performance

7. **Validación end-to-end**
   - Usuario hace query en `/api/chat/`
   - WorkflowRun se crea automáticamente
   - Usuario ve acción en `/actions/`
   - Administrador ve métricas en `/api/metrics/`

---

## 11. Open Questions (para fase de implementación)

1. **¿Incluir detalles de n8n response en system_decisions?**
   - **Resolución propuesta**: Registrar metadata completa recibida de n8n en system_decisions

2. **¿Color coding exacto para cada estado en actions.html?**
   - Definido: completed (verde), failed (rojo), running (azul), pending_approval (amarillo)
   - **Resolución propuesta**: blocked\_\* y cancelled usan rojo (mismo tratamiento que failed)

3. **¿Formato de fecha en actions.html?**
   - **Resolución propuesta**: Formato absoluto "17/04/2026 14:32" (consistencia con resto de Personal Stock)

---

## 12. Future Work (MVP 2+)

1. **Real-time updates**: WebSocket para actualizar `/actions/` cuando cambia estado
2. **Advanced filtering**: Filtrar por agent, estado, rango de fechas en UI
3. **Export**: Descargar trazabilidad como CSV/JSON
4. **Retention policy**: Archivar registros > 90 días
5. **Metrics dashboard**: Visualizaciones gráficas (charts)
6. **Async traceability**: Migrar a Celery para alto volumen
7. **Audit log**: Registro de acciones administrativas

---

## 13. Validaciones

✅ **Consistencia con requirements.md**: Todos los requirements tienen diseño técnico detallado
✅ **Integración con specs completados**: Usa User model (spec 2), contrato de /api/chat/ (spec 3)
✅ **Decisiones de requirements respetadas**: Transacción separada síncrona, NO mock de n8n, sin retención MVP 1
✅ **Testing strategy apropiada**: NO PBT (justificado), unit tests + integration tests + template tests
✅ **Security considerations**: 5 vectores de ataque con mitigaciones
✅ **Performance optimization**: Índices, queries eficientes, estimación de volumen
✅ **Error handling completo**: 5 categorías de errores con estrategias de manejo
✅ **Deployment path claro**: 7 pasos desde estado actual a implementación completa
✅ **Robustez de comparaciones de perfil**: Usa constantes `User.Profile.*` en lugar de strings literales para evitar fragilidad por typos

---

## 14. Cambios aplicados en esta revisión

**Corrección solicitada por el usuario (2026-06-27):**

El usuario solicitó reemplazar comparaciones de perfil con strings literales (`'Administrador'`, `'Usuario IC'`) por constantes del modelo User (`User.Profile.ADMINISTRADOR`, `User.Profile.USUARIO_IC`) para evitar fragilidad por typos o cambios de naming.

**Cambios realizados:**

1. **PermissionChecker (Componente 3)**: Actualizada toda la clase para usar `User.Profile.ADMINISTRADOR` y `User.Profile.USUARIO_IC` en lugar de strings
2. **API Endpoints**: Actualizadas descripciones de permisos para especificar uso de constantes
3. **Error Handling**: Agregada nota en error de permisos sobre uso de constantes
4. **Implementation Notes**: Agregada sección completa "1. Uso de Constantes de Perfil (User.Profile)" con:
   - Ejemplos de uso correcto e incorrecto
   - Lista de todas las constantes disponibles del spec 2
   - Ubicaciones donde aplica
   - Beneficios (refactor-safe, type checking, autocompletado)
   - Nota sobre dependencia del spec 2
5. **Delivery Document**: Agregada Decisión 7 con contexto, resolución, impacto y ubicaciones afectadas

**Verificación:**

- ✅ El modelo User del spec 2 ya define `Profile` como `TextChoices` con las 5 constantes
- ✅ Todas las comparaciones de perfil en el design ahora usan constantes
- ✅ Documentado que si el modelo no expone las constantes, deben agregarse al spec 2

---

## 15. Próximos pasos

---

## 15. Próximos pasos

El design.md ha sido actualizado con la corrección solicitada (uso de constantes `User.Profile.*`). Esperando aprobación explícita del usuario antes de proceder a la fase de tasks.

Una vez aprobado:

1. Generar tasks.md (lista de tareas de implementación con subtareas)
2. Implementación tarea por tarea

---

**Estado:** design.md completado y corregido — esperando aprobación para continuar con tasks.md

**Fecha:** 2026-06-27
**Veredicto:** ✅ COMPLETADO (actualizado con corrección de constantes de perfil)
