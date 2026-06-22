# Devolución: Tasks Usuarios Demo Perfiles Permisos

**Fecha:** 2026-06-22
**Spec:** usuarios-demo-perfiles-permisos
**Fase:** Tasks
**Veredicto:** ✅ Listo para revisión y aprobación del usuario

---

## Documento Generado

**Ubicación:** `/Users/luciano/Desktop/PS-edit/.kiro/specs/usuarios-demo-perfiles-permisos/tasks.md`

**Estructura del plan:**

- 13 tareas principales
- 22 sub-tareas leaf ejecutables
- 13 waves en dependency graph
- 4 checkpoints de validación incremental
- 9 correctness properties implementadas como property tests

---

## Resumen Ejecutivo

El plan de implementación divide el spec en tareas verificables y secuenciales que cubren:

1. **Migración crítica del User Model** (Tareas 1-4)
   - Backup del superusuario existente
   - Custom User Model + Role Model
   - Migración a AbstractUser
   - Recreación del superusuario

2. **Sistema de permisos** (Tareas 5-6)
   - DatasetFilter con 9 correctness properties
   - Property tests, unit tests, performance test

3. **Base demo de usuarios** (Tareas 7-9)
   - Fixture con 100 usuarios (12 específicos + 88 ficticios)
   - Management command load_demo_users
   - Validación completa de carga

4. **Integración con frontend** (Tareas 10-11)
   - Exposición de perfil/roles en home
   - Configuración del admin panel

5. **Preparación para specs futuros** (Tarea 12-13)
   - Contrato para n8n (sin implementar)
   - Validación final completa

---

## Tareas Principales

### Tarea 1: Respaldar superusuario existente y preparar migración

**Sub-tareas:** 1
**Criticidad:** ⚠️ CRÍTICA

Crea un backup del superusuario actual (creado en tarea 9 del spec `base-django-login-home`) antes de aplicar la migración a AbstractUser. Este backup contiene email, password hash, is_staff e is_superuser para recrearlo después de la migración.

**Justificación:** Sin este backup, la migración a AbstractUser eliminaría el superusuario existente y se perdería acceso al sistema.

**Output:** `app/fixtures/superuser_backup.json`

---

### Tarea 2: Crear Custom User Model y Role Model

**Sub-tareas:** 4 (2 implementación + 2 property tests)
**Wave:** 1-2

Implementa el modelo User extendiendo AbstractUser con:

- Email como USERNAME_FIELD (único)
- 5 perfiles con choices
- 12 campos de negocio del brief
- Métodos helpers: `has_restricted_access()`, `can_access_restricted_content()`
- Índices en perfil y es_focus

Implementa el modelo Role con:

- 7 roles válidos con choices
- Relación ManyToMany con User

**Property tests incluidos:**

- Property 1: Email Uniqueness
- Property 2: Profile Assignment Persistence
- Property 3: Role Assignment for Usuario IC
- Property 4: Role Restriction for Non-Usuario IC

**Output:** `app/core/models.py` con User y Role

---

### Tarea 3: Configurar AUTH_USER_MODEL y aplicar migración

**Sub-tareas:** 3
**Wave:** 2-4
**Criticidad:** ⚠️ CRÍTICA

Actualiza settings.py con `AUTH_USER_MODEL = 'core.User'`, genera la migración inicial, la aplica, y luego recrea el superusuario desde el backup preservando las credenciales originales.

**Comandos clave:**

```bash
python manage.py makemigrations
python manage.py migrate
# Script custom para recrear superusuario desde backup
```

**Validación:** Autenticación exitosa con credenciales previas del superusuario

**Output:**

- Tabla `core_user` en base de datos
- Superusuario preservado con perfil 'Administrador'

---

### Tarea 4: Checkpoint - Validar migración de User Model

**Tipo:** Checkpoint manual
**Wave:** 5

Punto de validación incremental para verificar que:

- Superusuario puede autenticarse correctamente
- Todas las tablas existen (core_user, core_role, core_user_roles)
- No hay errores de migración pendientes

**Acción:** Preguntar al usuario si puede continuar o hay problemas

---

### Tarea 5: Implementar DatasetFilter para permisos por perfil

**Sub-tareas:** 4 (1 implementación + 3 testing)
**Wave:** 5-6

Crea la clase `DatasetFilter` en `app/core/permissions.py` con:

- Método `filter_by_profile(user, dataset_records)`
- Método `is_record_restricted(record, user)`
- Filtrado case-insensitive por substrings en campo 'destinatario'
- Restricciones: "macro", "macroestructura", "líderes", "lideres"
- Solo aplicable a perfil Usuario (otros perfiles ven todo)

**Property tests incluidos:**

- Property 5: Dataset Filtering by Restricted Substrings
- Property 6: Dataset Access for Privileged Profiles

**Unit tests incluidos:**

- Usuario sin perfil (ValueError)
- Dataset vacío, destinatario None
- Case-insensitive matching

**Performance test:**

- Filtro debe ejecutar en <50ms con dataset completo (~5.300 registros)

**Output:** `app/core/permissions.py` con DatasetFilter

---

### Tarea 6: Checkpoint - Validar DatasetFilter

**Tipo:** Checkpoint manual
**Wave:** 7

Punto de validación para verificar:

- Todos los tests de DatasetFilter pasan
- Filtro excluye correctamente contenido restringido
- Perfiles privilegiados acceden a todo
- Performance <50ms

**Acción:** Preguntar al usuario si puede continuar

---

### Tarea 7: Generar fixture con 100 usuarios demo

**Sub-tareas:** 2 (1 generación + 1 validation tests)
**Wave:** 7-8

Crea `app/fixtures/demo_users.json` con:

- **12 usuarios específicos** con datos exactos del Requirement 2:
  - Luciano Zurlo (Administrador, Diseñador+Desarrollador)
  - Diego Ferrari (Usuario IC, Redactor)
  - Sara Astudillo (Usuario IC, Diseñador)
  - Martín Caso (Usuario IC, Productor)
  - Sebastián Álvarez Hincaipié (Usuario IC, Productor)
  - Emiliano Zabuski (Usuario IC, Redactor)
  - Jonathan Ferraro (Usuario IC, Gerente Cultura)
  - Luciana Dau (Usuario IC, Gerente IC)
  - Pablo Giglio (Usuario)
  - Javier Vulich (Usuario)
  - Sebastián Marzico (Usuario)
  - Santiago Gugger (Usuario)

- **88 usuarios ficticios** con:
  - Nombres y apellidos argentinos realistas
  - Emails: `demo.user{N}@personalstock.local` (N=13 a 100)
  - Distribución: 15+ Usuario IC, 30+ Usuario, resto variado
  - Roles solo asignados a Usuario IC
  - Al menos un usuario por cada uno de los 7 roles
  - memoria_habilitada = true por defecto

**Unit tests incluidos:**

- Total == 100 usuarios
- Presencia de 12 específicos
- Distribución mínima por perfil
- Emails únicos
- Roles solo en Usuario IC
- Al menos un usuario por cada rol

**Output:** `app/fixtures/demo_users.json` (fixture Django)

---

### Tarea 8: Implementar management command load_demo_users

**Sub-tareas:** 3 (1 implementación + 2 testing)
**Wave:** 8-9

Crea comando Django en `app/core/management/commands/load_demo_users.py` con:

- Opción `--fixture` para cargar desde JSON
- Opción `--csv` para cargar desde CSV (opcional)
- Opción `--dry-run` para validar sin cargar

**Validaciones obligatorias:**

- Total usuarios == 100
- Presencia de 12 usuarios específicos
- Campos obligatorios: first_name, last_name, email, perfil
- Emails únicos
- Perfiles válidos (uno de los 5)
- Roles válidos si perfil == Usuario IC
- Roles vacíos si perfil != Usuario IC

**Manejo de errores:** Rechazo atómico con mensaje descriptivo

**Property tests incluidos:**

- Property 7: Profile Validation
- Property 8: Invalid Role Assignment Rejection
- Property 9: CSV Load Rejection on Missing Fields

**Integration test:** Carga end-to-end desde fixture

**Output:** `app/core/management/commands/load_demo_users.py`

---

### Tarea 9: Checkpoint - Validar carga de usuarios demo

**Tipo:** Checkpoint manual + comando
**Wave:** 10

Ejecuta el comando de carga y valida:

```bash
python manage.py load_demo_users --fixture fixtures/demo_users.json
```

Verificar:

- 100 usuarios cargados correctamente
- Autenticación con usuario específico funciona
- Roles asignados correctamente a Usuario IC

**Acción:** Preguntar al usuario si puede continuar

---

### Tarea 10: Exponer perfil y roles en sistema de autenticación

**Sub-tareas:** 3 (2 implementación + 1 integration test)
**Wave:** 10-11

Actualiza vista de home y template para:

- Agregar `user.perfil` al contexto de la vista
- Agregar `user.roles.all()` al contexto
- Mostrar perfil visible en home.html
- Mostrar roles (si perfil == Usuario IC)

**Integration test:** Verificar perfil/roles en contexto después de autenticación

**Output:**

- `app/core/views.py` modificado
- `templates/home.html` modificado

---

### Tarea 11: Actualizar Django admin para User y Role models

**Sub-tareas:** 1
**Wave:** 11

Registra User y Role en admin panel con:

- UserAdmin extendiendo admin.ModelAdmin
- Fieldsets con campos custom
- list_display, list_filter, search_fields configurados
- RoleAdmin básico

**Output:** `app/core/admin.py` modificado

---

### Tarea 12: Preparar contrato para exposición a n8n

**Sub-tareas:** 1
**Wave:** 12

Documenta (sin implementar) la estructura de payload user para n8n:

```python
{
  "email": "string",
  "perfil": "string",
  "roles": ["string"],
  "first_name": "string",
  "last_name": "string"
}
```

**Nota:** La implementación real se hará en spec `home-chat-orchestrator-contract`

**Output:** `app/core/contracts/n8n_user_payload.py` (documentación)

---

### Tarea 13: Final checkpoint - Validación completa del spec

**Tipo:** Checkpoint manual + test suite
**Wave:** 13

Ejecuta validación completa:

- Suite completa de tests (property + unit + integration)
- Cobertura ≥90% en models.py y permissions.py
- Autenticación con superusuario y 3+ usuarios demo
- DatasetFilter funciona correctamente
- Admin panel muestra User y Role

**Acción:** Solicitar aprobación final del usuario

---

## Dependency Graph

### Ejecución Serializada (Orden de Implementación)

**Importante:** Aunque el dependency graph con waves muestra qué tareas podrían ejecutarse en paralelo en un entorno automatizado, la implementación real de este spec se ejecuta **serializada**: una sub-tarea por sesión de Claude Code, en orden secuencial.

**Orden de ejecución:**

```
1.1 → 2.1 → 2.2 → 2.3 → 2.4 → 3.1 → 3.2 → 3.3 → 4 (checkpoint) →
5.1 → 5.2 → 5.3 → 5.4 → 6 (checkpoint) →
7.1 → 7.2 → 8.1 → 8.2 → 8.3 → 9 (checkpoint) →
10.1 → 10.2 → 10.3 → 11.1 → 12.1 → 13 (checkpoint final)
```

### Waves de Referencia Técnica

El siguiente grafo solo sirve como referencia para visualizar dependencias lógicas:

```
Wave 0:  [1.1] ← Backup superusuario (CRÍTICO)
         ↓
Wave 1:  [2.1, 2.3] ← User Model + Role Model en paralelo
         ↓
Wave 2:  [2.2, 2.4, 3.1] ← Property tests + settings.py
         ↓
Wave 3:  [3.2] ← Migración
         ↓
Wave 4:  [3.3] ← Recrear superusuario
         ↓
Wave 5:  [5.1] ← DatasetFilter
         ↓
Wave 6:  [5.2, 5.3, 5.4] ← Tests de DatasetFilter en paralelo
         ↓
Wave 7:  [7.1] ← Fixture 100 usuarios
         ↓
Wave 8:  [7.2, 8.1] ← Tests fixture + comando en paralelo
         ↓
Wave 9:  [8.2, 8.3] ← Tests comando en paralelo
         ↓
Wave 10: [10.1] ← Vista home
         ↓
Wave 11: [10.2, 10.3, 11.1] ← Template + tests + admin en paralelo
         ↓
Wave 12: [12.1] ← Contrato n8n
```

**Total waves:** 13
**Tareas leaf:** 22
**Tareas en paralelo máximo:** 3 (wave 11)

---

## Testing Strategy

### Distribución de Cobertura

- **40% Property-Based Testing** (9 properties con hypothesis)
  - 100 iterations por property
  - Invariantes universales (unicidad, persistencia, validación)
  - **OBLIGATORIAS** (no opcionales)

- **40% Unit Tests**
  - Validación de 12 usuarios específicos
  - Distribución por perfiles
  - Edge cases de DatasetFilter
  - **OBLIGATORIAS** (no opcionales)

- **20% Integration Tests**
  - Comando load_demo_users end-to-end
  - Autenticación + exposición de perfil/roles
  - Filtro con dataset real
  - **OBLIGATORIAS** (no opcionales)

**Nota:** Todas las tareas de testing son OBLIGATORIAS en este proyecto, siguiendo el enfoque de validación robusta establecido en el spec `base-django-login-home`.

### Property Tests Implementados

| Property                               | Tarea | Validates         |
| -------------------------------------- | ----- | ----------------- |
| 1. Email Uniqueness                    | 2.2   | Req 1.6, 8.2      |
| 2. Profile Persistence                 | 2.2   | Req 3.2, 3.3      |
| 3. Role Assignment for Usuario IC      | 2.4   | Req 4.1, 4.3, 4.4 |
| 4. Role Restriction for Non-Usuario IC | 2.4   | Req 4.2           |
| 5. Dataset Filtering                   | 5.2   | Req 5.1-5.5       |
| 6. Dataset Access for Privileged       | 5.2   | Req 5.7           |
| 7. Profile Validation                  | 8.2   | Req 8.3           |
| 8. Invalid Role Rejection              | 8.2   | Req 8.4           |
| 9. CSV Load Rejection                  | 8.2   | Req 7.5           |

---

## Tareas Opcionales

**No hay tareas opcionales en este spec.** Todas las tareas, incluyendo los tests, son OBLIGATORIAS.

Este proyecto sigue el enfoque de validación robusta establecido en el spec `base-django-login-home`, donde los property tests, unit tests e integration tests son parte integral de la implementación, no opcionales.

---

## Consideraciones Críticas

### 1. Migración del Superusuario

**⚠️ CRÍTICO:** La tarea 1.1 NO puede omitirse.

Este spec modifica el modelo User después de que ya existe un superusuario creado en el spec `base-django-login-home` (tarea 9). Sin el backup y recreación, se pierde acceso al admin panel.

**Secuencia obligatoria:**

1. Backup del superusuario actual (tarea 1.1)
2. Aplicar migración a AbstractUser (tarea 3.2)
3. Recrear superusuario desde backup (tarea 3.3)
4. Validar autenticación (checkpoint tarea 4)

### 2. Performance del Filtro

El DatasetFilter debe ejecutar en **<50ms** sobre el dataset completo (~5.300 registros) según Requirement 10.3. La tarea 5.4 valida esto con un performance test.

Si el test falla, optimizar con:

- Cache de user.perfil
- List comprehension en lugar de loops
- Compilar regex para matching

### 3. Fixture Realista

Los 88 usuarios ficticios deben tener:

- Nombres argentinos realistas (no "User1", "User2")
- Emails con dominio `@personalstock.local`
- Distribución coherente de perfiles y roles

Esto simula un entorno de producción real y facilita testing manual.

### 7. Roles Variados

**Requisito:** Cada uno de los 7 roles debe estar asignado al menos a un usuario Usuario IC.

Esto garantiza que se pueden testear todos los roles en specs futuros que dependan de roles específicos (ej: asignación de Focus, aprobadores).

---

## Archivos Generados/Modificados

### Nuevos

1. `app/fixtures/superuser_backup.json` - Backup del superusuario
2. `app/fixtures/demo_users.json` - 100 usuarios demo
3. `app/core/permissions.py` - DatasetFilter
4. `app/core/management/commands/load_demo_users.py` - Comando de carga
5. `app/core/contracts/n8n_user_payload.py` - Contrato n8n (docs)
6. Tests:
   - `app/core/tests/test_models.py` - Property tests User/Role
   - `app/core/tests/test_permissions.py` - Property/unit tests DatasetFilter
   - `app/core/tests/test_commands.py` - Property/integration tests comando
   - `app/core/tests/test_views.py` - Integration tests vistas

### Modificados

1. `app/core/models.py` - User y Role models
2. `app/config/settings.py` - AUTH_USER_MODEL
3. `app/core/views.py` - Exposición perfil/roles
4. `templates/home.html` - Mostrar perfil/roles
5. `app/core/admin.py` - UserAdmin y RoleAdmin

---

## Comandos de Validación Clave

```bash
# Backup superusuario (tarea 1.1)
python manage.py dumpdata auth.user --indent 2 > app/fixtures/superuser_backup.json

# Migración (tareas 3.1-3.2)
python manage.py makemigrations
python manage.py migrate

# Cargar usuarios demo (tarea 9)
python manage.py load_demo_users --fixture fixtures/demo_users.json

# Dry-run para validar fixture sin cargar
python manage.py load_demo_users --fixture fixtures/demo_users.json --dry-run

# Test suite completa (tarea 13)
python manage.py test app.core.tests
pytest app/core/tests/ -v --hypothesis-show-statistics

# Cobertura de código
coverage run --source='app/core' manage.py test app.core.tests
coverage report
```

---

## Fuera de Alcance (Specs Futuros)

Los siguientes componentes NO se implementan en este spec:

1. **Integración con n8n** → Spec `home-chat-orchestrator-contract`
   - Solo se documenta el contrato de payload user

2. **Implementación del agente RAG** → Spec `agente-rag-historial-mails`
   - DatasetFilter está listo para ser consumido

3. **Trazabilidad de permisos** → Spec `acciones-trazabilidad-metricas`
   - Logs de quién accedió a qué contenido

4. **Respuesta segura del RAG** → Spec `agente-rag-historial-mails`
   - Mensaje cuando se detecta contenido restringido

5. **Normalización de áreas_focus** → Spec futuro
   - Por ahora es string separado por comas

---

## Próximos Pasos

1. ✅ **Requirements aprobados**
2. ✅ **Design completado y corregido**
3. ✅ **Tasks generado y aprobado con correcciones**
4. ➡️ **Listo para implementación serializada (1.1 → 2.1 → 2.2 → ... → 13)**

---

## Veredicto Final

✅ **Tasks completado, corregido y APROBADO**
✅ **Sin errores de diagnóstico**
✅ **22 tareas leaf distribuidas en 13 waves**
✅ **4 checkpoints de validación incremental**
✅ **9 correctness properties identificadas y distribuidas**

El plan de implementación está completo y optimizado para ejecución eficiente. Incluye:

- Backup crítico del superusuario antes de migración
- 13 tareas principales con 22 sub-tareas ejecutables
- Testing robusto: property tests (40%) + unit tests (40%) + integration tests (20%)
- 4 checkpoints para validación incremental
- Dependency graph con 13 waves optimizadas para paralelismo
- Comandos de validación específicos por tarea

**⚠️ Consideración crítica:** La tarea 1.1 (backup superusuario) es OBLIGATORIA y no puede omitirse.

**Estado:** Esperando aprobación explícita del usuario antes de comenzar implementación.

**Siguiente paso:** Usuario revisa tasks.md y aprueba o solicita ajustes.

---

## Correcciones Aplicadas Según Feedback del Usuario

### 1. Checkpoints Automáticos (No Interactivos)

**Antes:** Los checkpoints decían "Preguntar al usuario si hay problemas o puede continuar"

**Después:** Los checkpoints ejecutan verificaciones programáticas y "Reportan resultados de la verificación punto por punto"

**Justificación:** Los checkpoints no solicitan input interactivo durante la implementación. La validación humana se realiza en el paso posterior de "verificación cruzada" (paso 3.5 del workflow).

**Tareas afectadas:** 4, 6, 9, 13

### 2. Tests OBLIGATORIOS (No Opcionales)

**Antes:** Las tareas de testing estaban marcadas con `*` como opcionales

**Después:** Todas las tareas de testing son OBLIGATORIAS, sin marca opcional

**Justificación:** Este proyecto sigue el enfoque de validación robusta establecido en el spec `base-django-login-home`, donde los property tests, unit tests e integration tests son parte integral de la implementación.

**Tareas afectadas:** 2.2, 2.4, 5.2, 5.3, 5.4, 7.2, 8.2, 8.3, 10.3

### 3. Ejecución Serializada (No Paralela)

**Antes:** El Task Dependency Graph presentaba waves para ejecución paralela

**Después:** Se aclaró que el grafo es solo referencia técnica. La ejecución real es serializada: 1.1 → 2.1 → 2.2 → ... → 13

**Justificación:** La implementación va una subtarea por sesión de Claude Code, en orden secuencial. No se ejecuta nada en paralelo.

**Impacto:** Sección "Task Dependency Graph" actualizada con nota explicativa
