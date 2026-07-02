# Devolución: Tasks - Spec 4 (acciones-trazabilidad-metricas)

**Fecha:** 2026-06-27
**Spec:** acciones-trazabilidad-metricas
**Fase:** tasks
**Veredicto:** ✅ COMPLETADO

---

## 1. Qué se generó

Se generó el documento `tasks.md` para el spec 4: acciones-trazabilidad-metricas, con el plan de implementación completo organizado en 15 tareas principales con subtareas y 5 checkpoints de validación.

### Archivo creado

- `.kiro/specs/acciones-trazabilidad-metricas/tasks.md`

### Estructura del documento

1. **Overview**: Visión general del plan de implementación con énfasis en uso de constantes User.Profile
2. **Tasks**: 15 tareas principales organizadas en 7 waves de implementación
3. **Notes**: Lenguaje (Python/Django), reglas críticas sobre constantes de perfil, transacción separada, sin PBT, ejecución serial
4. **Task Dependency Graph**: Grafo JSON proporcionado solo como referencia - implementación procede serialmente

---

## 2. Estructura de implementación

### 2.1 Waves de implementación

**Wave 0-1: Modelos y Migraciones** (Tareas 1.1, 1.2, 1.3)

- Crear WorkflowRun model con 12 estados y 4 índices
- Crear MetricEvent model con 3 tipos de eventos
- Generar y aplicar migraciones Django

**Wave 2: Service Classes** (Tareas 3.1, 3.2, 3.3)

- TraceabilityManager: CRUD con transacciones separadas síncronas
- MetricsAggregator: Agregación SQL eficiente
- PermissionChecker: Control de acceso usando **User.Profile constants** (NO strings)

**Wave 3-4: Integración con API** (Tareas 5.1, 5.2, 7.1, 7.2, 7.3)

- Modificar chat_view para trazabilidad automática
- Incluir metadata en response payload
- Crear 3 endpoints REST con permisos por perfil

**Wave 5-7: Template y Página** (Tareas 7.4, 9.1-9.5)

- Crear actions.html con color coding por estado
- Crear CSS con estilos para estados
- Crear JS para modal de detalles
- Crear view y URL route

**Wave 8-9: Tests Completos** (Tareas 11.1-14.2)

- Unit tests: TraceabilityManager, MetricsAggregator
- Integration tests: API endpoints, chat_view traceability
- Model tests: Índices, state transitions
- Template tests: Rendering, color coding, paginación

### 2.2 Checkpoints de validación

Cada checkpoint ejecuta verificaciones específicas y reporta resultados punto por punto, sin esperar input interactivo del usuario:

1. **Checkpoint después de Task 1.3**: Verificar database setup (migraciones aplicadas, índices creados)
2. **Checkpoint después de Task 3.3**: Verificar service classes (métodos presentes, transacciones correctas)
3. **Checkpoint después de Task 5.2**: Test traceability integration (WorkflowRun creado en cada request)
4. **Checkpoint después de Task 7.4**: Test API endpoints (datos correctos, permisos funcionando, paginación)
5. **Checkpoint después de Task 9.5**: Test actions page (rendering correcto, color coding, login requerido)
6. **Checkpoint después de Task 14.2** (final): End-to-end validation (flujo completo, >80% test coverage)

---

## 3. Tareas principales generadas

### Task 1: Create Django models (3 subtareas)

- 1.1: WorkflowRun model con ExecutionState TextChoices, 12 estados, 4 índices, método add_state_transition()
- 1.2: MetricEvent model con EventType TextChoices, 3 tipos, 2 índices
- 1.3: Migrations (makemigrations, migrate, verify)

### Task 3: Implement service classes (3 subtareas)

- 3.1: TraceabilityManager con 4 métodos (create_run, update_run_agent_selection, complete_run, fail_run), transaction.atomic() separada, error logging
- 3.2: MetricsAggregator con 2 métodos (get_summary_metrics usando ORM aggregation, record_metric_event)
- 3.3: **PermissionChecker con 4 métodos usando User.Profile constants** (can_access_metrics, can_access_admin_actions, get_user_runs_queryset, get_all_runs_queryset)

**CRÍTICO en Task 3.3**: Especifica explícitamente que se deben usar `User.Profile.ADMINISTRADOR` y `User.Profile.USUARIO_IC` (NO strings literales) en todas las comparaciones de perfil.

### Task 5: Integrate traceability into /api/chat/ (2 subtareas)

- 5.1: Modificar chat_view para llamar TraceabilityManager en inicio, éxito, y todos los error handlers
- 5.2: Agregar metadata object al response payload

### Task 7: Implement API endpoints (4 subtareas)

- 7.1: api_actions view con @login_required, paginación, error handling
- 7.2: api_metrics view con permission check usando PermissionChecker.can_access_metrics(), date filtering
- 7.3: api_admin_actions view con permission check usando PermissionChecker.can_access_admin_actions(), user_id filtering
- 7.4: Add URL routes a core/urls.py

### Task 9: Create actions template (5 subtareas)

- 9.1: actions.html con header, actions list, pagination, modal
- 9.2: actions.css con color coding (green: completed, red: failed/blocked/cancelled, blue: running, yellow: pending)
- 9.3: actions.js con showDetails() function
- 9.4: actions_page view con @login_required, paginación
- 9.5: Add URL route

### Tasks 11-14: Write comprehensive tests (8 subtareas - OBLIGATORIAS)

- 11.1-11.2: Unit tests para service classes (6 test cases)
- 12.1-12.3: Integration tests para API endpoints (9 test cases) - **Usan User.Profile constants en assertions**
  - **CRÍTICO**: Tests 12.2 y 12.3 validan permisos (Usuario no accede a métricas ni a acciones de otros). Son obligatorios para validación de seguridad.
- 13.1: Integration tests para chat_view traceability (6 test cases)
- 14.1-14.2: Model y template tests (7 test cases)

**Total**: 25+ test cases cubriendo unit, integration, model, y template testing. **Todos son obligatorios** - los tests de permisos (12.2, 12.3) son críticos y no pueden omitirse.

---

## 4. Reglas críticas documentadas

### Uso de Constantes User.Profile (CRÍTICO)

El tasks.md enfatiza en múltiples lugares que todas las comparaciones de perfil deben usar constantes del modelo User:

**En Notes section**:

> **User.Profile Constants**: All profile comparisons MUST use `User.Profile.ADMINISTRADOR` and `User.Profile.USUARIO_IC` constants from the User model (spec usuarios-demo-perfiles-permisos), NOT literal strings like `'Administrador'` or `'Usuario IC'`. This applies to PermissionChecker service class, API views, and all tests.

**En Task 3.3** (PermissionChecker):

> **CRITICAL**: Import `from core.models import User` and use `User.Profile.ADMINISTRADOR` and `User.Profile.USUARIO_IC` constants (NOT literal strings) for all profile comparisons

**En Task 12.2** (api_metrics tests):

> **CRITICAL**: Use User.Profile.ADMINISTRADOR and User.Profile.USUARIO_IC constants in test assertions, NOT literal strings

**En Task 12.3** (api_admin_actions tests):

> **CRITICAL**: Use User.Profile.ADMINISTRADOR constant in test setup and assertions, NOT literal string

### Otras reglas importantes

1. **Transacción Separada Síncrona**: TraceabilityManager usa `transaction.atomic()` - errores NO deben bloquear respuesta al usuario
2. **No Property-Based Testing**: Usa solo unit tests + integration tests (justificado: side effects, CRUD, integración con infraestructura)
3. **Test Coverage Goal**: >80% para service classes, 100% para API endpoints

---

## 5. Task Dependency Graph

El grafo de dependencias se proporciona como **referencia únicamente** para comprender las dependencias entre tareas. La implementación debe proceder **serialmente**, una subtarea por sesión de Claude Code, en orden numérico (1.1 → 1.2 → 1.3 → 2 → 3.1 → ...). No se ejecuta nada en paralelo.

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] }, // Modelos (referencia)
    { "id": 1, "tasks": ["1.3"] }, // Migraciones
    { "id": 2, "tasks": ["3.1", "3.2", "3.3"] }, // Service classes (referencia)
    { "id": 3, "tasks": ["5.1"] }, // chat_view integration
    { "id": 4, "tasks": ["5.2", "7.1", "7.2", "7.3"] }, // Response metadata + API endpoints (referencia)
    { "id": 5, "tasks": ["7.4", "9.1", "9.2", "9.3"] }, // URL routes + template files (referencia)
    { "id": 6, "tasks": ["9.4"] }, // actions_page view
    { "id": 7, "tasks": ["9.5", "11.1", "11.2"] }, // URL route + unit tests (referencia)
    { "id": 8, "tasks": ["12.1", "12.2", "12.3", "13.1"] }, // Integration tests (referencia)
    { "id": 9, "tasks": ["14.1", "14.2"] } // Model + template tests (referencia)
  ]
}
```

**Nota importante**: El grafo muestra dependencias conceptuales pero NO autoriza ejecución paralela. Implementar secuencialmente en orden numérico.

---

## 6. Validaciones

✅ **Consistencia con design.md**: Todas las tareas implementan componentes definidos en el design
✅ **Consistencia con requirements.md**: Cada tarea referencia requirements específicos
✅ **Uso de User.Profile constants**: Documentado en múltiples lugares (notes, tasks críticas)
✅ **Estructura de waves**: Permite paralelización donde sea posible
✅ **Checkpoints de validación**: 6 checkpoints para validación incremental
✅ **Test coverage completo**: 25+ test cases (unit + integration + model + template)
✅ **Sin property-based testing**: Justificado en notes (side effects, CRUD, integración)
✅ **Atomic transactions**: TraceabilityManager implementa transacciones separadas síncronas

---

## 7. Dependencias de specs

**Este spec depende de** (ya completados):

1. `base-django-login-home`: Autenticación, sesiones, templates base
2. `usuarios-demo-perfiles-permisos`: User model con campo `perfil` como TextChoices (User.Profile.ADMINISTRADOR, etc.)
3. `home-chat-orchestrator-contract`: Endpoint `/api/chat/`, estructura de metadata en Response_Payload

**Specs que dependen de este** (quedan pendientes):

1. `rag-mails-dataset-permissions`: Debe registrar trazabilidad en cada consulta RAG
2. `trigger-comunicaciones-email`: Debe registrar trazabilidad en cada trigger
3. `memoria-feedback-correcciones`: Usará WorkflowRun para historial conversacional

---

## 8. Próximos pasos

El tasks.md está completo y listo para implementación.

**Orden recomendado de ejecución**:

1. Implementar secuencialmente en orden numérico (1.1 → 1.2 → 1.3 → 2 → 3.1 → 3.2 → ...)
2. Una subtarea por sesión de Claude Code
3. Ejecutar checkpoints después de las tareas indicadas (1.3, 3.3, 5.2, 7.4, 9.5, 14.2)
4. Checkpoints reportan resultados punto por punto sin esperar input interactivo
5. Validar cada checkpoint antes de continuar
6. Ejecutar tests completos al final (Task 15 checkpoint)

**Implementación**:

- Usar Claude Code en modo `plan` (una tarea por sesión)
- Validar cada tarea contra su criterio de aceptación
- Ejecutar tests después de cada wave de implementación
- Commit atómico por tarea completada

---

## 9. Corrección global de estructura de tests (2026-07-01)

**Motivo:** Las tareas 11.2, 12.1, 12.2, 12.3, 13.1, 14.1 y 14.2 en el tasks.md original referenciaban rutas del tipo `core/tests/test_*.py` (paquete `tests/`). Esto es incorrecto para este proyecto.

**Decisión preexistente (devolución 70):** `docs/devoluciones/70-validacion-home-chat-orchestrator-contract-tarea-2.3.md` documenta que Python no permite que coexistan `core/tests.py` y `core/tests/` en la misma carpeta (conflicto de import). El proyecto adoptó el módulo único `app/core/tests.py` desde entonces. Aproximadamente 15 devoluciones posteriores referencian tests con la ruta `core.tests.NombreDeClase`, consolidando esa decisión.

**Corrección aplicada:** Se actualizaron todas las líneas de encabezado de subtareas de testing para reemplazar las rutas `core/tests/test_*.py` por `core/tests.py (módulo único)` con referencia a la devolución 70:

| Tarea | Antes                                     | Después                                |
| ----- | ----------------------------------------- | -------------------------------------- |
| 11.2  | `in core/tests/test_traceability.py`      | `in core/tests.py (módulo único; ...)` |
| 12.1  | `in core/tests/test_api_endpoints.py`     | `in core/tests.py (módulo único; ...)` |
| 12.2  | `in core/tests/test_api_endpoints.py`     | `in core/tests.py (módulo único; ...)` |
| 12.3  | `in core/tests/test_api_endpoints.py`     | `in core/tests.py (módulo único; ...)` |
| 13.1  | `in core/tests/test_chat_traceability.py` | `in core/tests.py (módulo único; ...)` |
| 14.1  | `in core/tests/test_models.py`            | `in core/tests.py (módulo único; ...)` |
| 14.2  | `in core/tests/test_templates.py`         | `in core/tests.py (módulo único; ...)` |

La tarea 11.1 ya había sido corregida durante la validación de esa tarea (devolución 121).

**Impacto:** Ningún cambio de alcance ni de criterios de aceptación. Solo se corrigió la ruta del archivo destino. Los nombres de clases y tests dentro de cada tarea permanecen idénticos. Claude Code debe agregar nuevas clases `TestCase` al final de `app/core/tests.py` existente, sin crear ningún archivo ni paquete nuevo bajo `core/tests/`.

---

**Estado:** tasks.md completado — listo para implementación

**Fecha original:** 2026-06-27 | **Última actualización:** 2026-07-01 (corrección global de rutas de tests)
**Veredicto:** ✅ COMPLETADO
