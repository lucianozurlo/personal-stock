# Implementation Plan: Usuarios Demo, Perfiles y Permisos

## Overview

Este plan implementa el sistema completo de usuarios demo, perfiles, roles y filtrado de dataset histórico para Personal Stock MVP 1. La implementación extiende el modelo User de Django a partir de AbstractUser, crea una base demo de 100 usuarios (12 específicos + 88 ficticios), implementa 5 perfiles con permisos diferenciados, asigna roles a usuarios del perfil Usuario IC, y aplica restricciones de acceso al dataset histórico según perfil.

**Contexto crítico:** Este spec corre DESPUÉS de `base-django-login-home`, lo que significa que ya existe un superusuario creado en la base de datos (tarea 9 del spec 1). La migración a AbstractUser requiere preservar o recrear ese superusuario para no perder acceso al sistema.

**Enfoque de implementación:**

1. Respaldar datos del superusuario existente antes de migración
2. Crear Custom User Model extendiendo AbstractUser con campos de negocio
3. Aplicar migración que reemplaza auth_user por core_user
4. Recrear superusuario preservando credenciales
5. Implementar modelo Role y relación ManyToMany
6. Crear DatasetFilter para permisos por perfil
7. Generar fixture con 100 usuarios demo (12 específicos + 88 ficticios)
8. Implementar comando de carga load_demo_users
9. Exponer perfil/roles en templates y sistema de autenticación
10. Testing distribuido: property tests, unit tests, integration tests

## Tasks

- [ ] 1. Respaldar superusuario existente y preparar migración a Custom User Model
  - [x] 1.1 Crear script de backup del superusuario actual
    - Crear script que extraiga email, password hash, is_staff, is_superuser del superusuario actual
    - Guardar backup en `app/fixtures/superuser_backup.json`
    - Documentar en código que este backup se usará después de la migración
    - _Requirements: 1.6, 8.2 (email unique), contexto crítico del spec_

- [ ] 2. Crear Custom User Model y Role Model
  - [x] 2.1 Implementar User model extendiendo AbstractUser en `app/core/models.py`
    - Agregar campo `email` como EmailField unique (USERNAME_FIELD)
    - Agregar campo `perfil` con choices (5 perfiles)
    - Agregar campo `roles` como ManyToManyField a Role
    - Agregar campos de negocio: cargo, es_focus, areas_focus, es_aprobador_default, puede_aprobar, avatar_url, memoria_habilitada
    - Configurar USERNAME_FIELD = 'email' y REQUIRED_FIELDS = ['first_name', 'last_name']
    - Implementar métodos: has_restricted_access(), can_access_restricted_content()
    - Agregar índices en perfil y es_focus
    - _Requirements: 3.1, 3.2, 3.3, 8.1, 8.2, 8.5_

  - [x] 2.2 Write property test for User model
    - **Property 1: Email Uniqueness** - Para cualquier conjunto de usuarios creados, todos los emails deben ser únicos
    - **Property 2: Profile Assignment Persistence** - Para cualquier usuario con perfil válido, al guardarlo y recargarlo, el perfil persiste sin cambios
    - **Validates: Requirements 1.6, 3.2, 3.3, 8.2**

  - [x] 2.3 Implementar Role model en `app/core/models.py`
    - Agregar campo `name` con choices (7 roles) unique
    - Agregar campo `description` opcional
    - Configurar Meta: verbose_name, ordering
    - _Requirements: 4.1_

  - [x] 2.4 Write property test for Role assignment
    - **Property 3: Role Assignment for Usuario IC** - Para cualquier usuario con perfil "Usuario IC", debe permitir asignar cero o más roles válidos que persisten correctamente
    - **Property 4: Role Restriction for Non-Usuario IC** - Para cualquier usuario con perfil diferente de "Usuario IC", no debe tener roles asignados (roles.count() == 0)
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [ ] 3. Configurar AUTH_USER_MODEL y aplicar migración
  - [x] 3.1 Actualizar `app/config/settings.py`
    - Agregar `AUTH_USER_MODEL = 'core.User'`
    - Verificar que esta configuración está antes de cualquier referencia a User
    - _Requirements: 3.3, 3.4_

  - [x] 3.2 Generar y aplicar migración inicial
    - Ejecutar `python manage.py makemigrations`
    - Revisar migración generada (debe crear tabla core_user y core_role)
    - Aplicar migración con `python manage.py migrate`
    - _Requirements: 3.3_

  - [x] 3.3 Recrear superusuario desde backup
    - Crear script que lea `superuser_backup.json`
    - Recrear superusuario con mismo email y password hash
    - Asignar perfil 'Administrador' por defecto
    - Validar autenticación exitosa con credenciales previas
    - _Requirements: Contexto crítico del spec_

- [ ] 4. Checkpoint - Validar migración de User Model
  - Verificar que superusuario puede autenticarse correctamente
  - Verificar que tabla core_user existe con todos los campos
  - Verificar que tabla core_role existe
  - Verificar que tabla intermedia core_user_roles existe
  - Reportar resultados de la verificación punto por punto

- [ ] 5. Implementar DatasetFilter para permisos por perfil
  - [ ] 5.1 Crear clase DatasetFilter en `app/core/permissions.py`
    - Definir constante RESTRICTED_SUBSTRINGS = ['macro', 'macroestructura', 'líderes', 'lideres']
    - Implementar método classmethod filter_by_profile(user, dataset_records)
    - Implementar método classmethod is_record_restricted(record, user)
    - Aplicar filtrado case-insensitive por substring en campo 'destinatario'
    - Perfiles privilegiados (Administrador, Usuario IC, Heavy user, Macro) ven todo
    - Perfil Usuario excluye registros con substrings restringidas
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 10.1_

  - [ ] 5.2 Write property tests for DatasetFilter
    - **Property 5: Dataset Filtering by Restricted Substrings** - Para cualquier registro con destinatario que contenga substrings restringidas y usuario con perfil "Usuario", el filtro debe excluir ese registro
    - **Property 6: Dataset Access for Privileged Profiles** - Para cualquier registro (incluyendo restringidos) y usuario con perfil privilegiado, el filtro debe incluir ese registro
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.7**

  - [ ] 5.3 Write unit tests for DatasetFilter edge cases
    - Test con usuario sin perfil definido (debe lanzar ValueError)
    - Test con dataset vacío (debe retornar lista vacía)
    - Test con destinatario None o vacío (debe incluir registro)
    - Test case-insensitive matching (MACRO, Macro, macro)
    - _Requirements: 5.5, 10.1_

  - [ ] 5.4 Write performance test for DatasetFilter
    - Cargar dataset real desde `mails/output/relevamiento_enriquecido.json`
    - Ejecutar filter_by_profile con usuario perfil Usuario
    - Validar que ejecuta en <50ms
    - _Requirements: 10.3_

- [ ] 6. Checkpoint - Validar DatasetFilter
  - Ejecutar todos los tests de DatasetFilter
  - Verificar que filtro excluye correctamente contenido restringido
  - Verificar que perfiles privilegiados acceden a todo
  - Reportar resultados de la verificación punto por punto

- [ ] 7. Generar fixture con 100 usuarios demo
  - [ ] 7.1 Crear fixture JSON con 100 usuarios en `app/fixtures/demo_users.json`
    - Incluir los 12 usuarios específicos con datos exactos del Requirement 2
    - Generar 88 usuarios ficticios adicionales con nombres argentinos realistas
    - Distribuir perfiles: al menos 15 Usuario IC, al menos 30 Usuario, resto distribuido
    - Asignar roles solo a usuarios con perfil Usuario IC
    - Asignar roles variados a Usuario IC (al menos un usuario por cada rol de los 7)
    - Configurar memoria_habilitada = true por defecto
    - Validar que todos los emails son únicos
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1-2.12, 4.1, 4.2, 8.5_

  - [ ] 7.2 Write unit tests para validar fixture
    - Test total de usuarios == 100
    - Test presencia de 12 usuarios específicos con email correcto
    - Test distribución mínima por perfil (15+ Usuario IC, 30+ Usuario)
    - Test emails únicos
    - Test roles solo en Usuario IC
    - Test al menos un usuario por cada uno de los 7 roles
    - _Requirements: 1.1, 1.3, 1.4, 1.6, 2.1-2.12, 4.2_

- [ ] 8. Implementar management command load_demo_users
  - [ ] 8.1 Crear comando en `app/core/management/commands/load_demo_users.py`
    - Implementar opción --fixture para cargar desde JSON
    - Implementar opción --csv para cargar desde CSV (opcional)
    - Implementar opción --dry-run para validar sin cargar
    - Validar total de usuarios == 100
    - Validar presencia de 12 usuarios específicos
    - Validar campos obligatorios: first_name, last_name, email, perfil
    - Validar emails únicos
    - Validar perfiles válidos (uno de los 5)
    - Validar roles válidos si perfil == Usuario IC
    - Validar roles vacíos si perfil != Usuario IC
    - Rechazar carga completa si hay errores, con mensaje descriptivo
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 8.3, 8.4_

  - [ ] 8.2 Write property test for load_demo_users validation
    - **Property 7: Profile Validation** - Para cualquier intento de crear usuario con perfil inválido, Django debe rechazar con ValidationError
    - **Property 8: Invalid Role Assignment Rejection** - Para cualquier intento de asignar rol inválido a Usuario IC, Django debe rechazar con ValidationError
    - **Property 9: CSV Load Rejection on Missing Fields** - Para cualquier CSV con campos obligatorios faltantes, el comando debe rechazar la carga completa
    - **Validates: Requirements 7.5, 8.3, 8.4**

  - [ ] 8.3 Write integration test para load_demo_users end-to-end
    - Test carga exitosa desde fixture demo_users.json
    - Test validación de 12 usuarios específicos después de carga
    - Test dry-run no crea usuarios
    - Test rechazo de fixture con usuario faltante
    - Test rechazo de fixture con email duplicado
    - _Requirements: 7.2, 7.3, 7.4, 7.6_

- [ ] 9. Checkpoint - Validar carga de usuarios demo
  - Ejecutar `python manage.py load_demo_users --fixture fixtures/demo_users.json`
  - Validar que los 100 usuarios se cargaron correctamente
  - Validar autenticación con uno de los 12 usuarios específicos
  - Verificar que roles se asignaron correctamente a Usuario IC
  - Reportar resultados de la verificación punto por punto

- [ ] 10. Exponer perfil y roles en sistema de autenticación
  - [ ] 10.1 Actualizar vista de home para incluir perfil y roles en contexto
    - Modificar `app/core/views.py` para agregar user.perfil y user.roles.all() al contexto
    - Verificar que datos se exponen correctamente en session
    - _Requirements: 9.1, 9.2, 9.3_

  - [ ] 10.2 Actualizar template home.html para mostrar perfil y roles
    - Agregar sección visible que muestre perfil del usuario actual
    - Agregar sección que muestre roles (si perfil == Usuario IC)
    - Mantener diseño consistente con template existente
    - _Requirements: 9.3, 3.4_

  - [ ] 10.3 Write integration test para exposición de perfil/roles
    - Test autenticación + acceso a home incluye perfil en contexto
    - Test usuario con roles ve sus roles en template
    - Test usuario sin roles no ve sección de roles
    - _Requirements: 9.1, 9.2, 9.3_

- [ ] 11. Actualizar Django admin para User y Role models
  - [ ] 11.1 Registrar User y Role en `app/core/admin.py`
    - Configurar UserAdmin extendiendo de admin.ModelAdmin
    - Agregar campos custom al fieldset (perfil, roles, cargo, etc.)
    - Configurar list_display con campos relevantes
    - Configurar list_filter por perfil y es_focus
    - Configurar search_fields por email, first_name, last_name
    - Registrar RoleAdmin con list_display y search
    - _Requirements: 3.5, 8.1_

- [ ] 12. Preparar contrato para exposición a n8n (sin implementar integración)
  - [ ] 12.1 Documentar estructura de payload user para n8n
    - Crear archivo `app/core/contracts/n8n_user_payload.py` con estructura de datos
    - Definir schema: { "email", "perfil", "roles": [], "first_name", "last_name" }
    - Agregar comentario: "Este contrato se implementará en spec home-chat-orchestrator-contract"
    - _Requirements: 9.4, 9.5_

- [ ] 13. Final checkpoint - Validación completa del spec
  - Ejecutar suite completa de tests (property + unit + integration)
  - Verificar cobertura de código ≥90% en models.py y permissions.py
  - Validar autenticación con superusuario original
  - Validar autenticación con al menos 3 usuarios demo diferentes
  - Validar que DatasetFilter excluye correctamente contenido para perfil Usuario
  - Validar que perfiles privilegiados acceden a todo el dataset
  - Validar que admin panel muestra User y Role correctamente
  - Reportar resultados de la verificación punto por punto

## Notes

- **Todas las tareas de testing son OBLIGATORIAS** - Este proyecto sigue el enfoque de validación robusta establecido en el spec `base-django-login-home`, donde los tests son parte integral de la implementación, no opcionales
- **Ejecución serializada**: Las tareas se ejecutan una por una, en orden secuencial (1.1 → 2.1 → 2.2 → ... → 13). Una sub-tarea por sesión de Claude Code. No se ejecuta nada en paralelo
- **Checkpoints automáticos**: Los 4 checkpoints (tareas 4, 6, 9, 13) ejecutan verificaciones y reportan resultados punto por punto. No solicitan input interactivo durante la implementación
- **Testing distribuido**: Los property tests y unit tests se ejecutan inmediatamente después de implementar cada componente, no todo al final
- **Migración crítica**: La tarea 1 (backup de superusuario) es CRÍTICA y no debe omitirse, ya que este spec modifica el modelo User después de que ya existe un superusuario en la base de datos
- **Property-Based Testing**: Se implementan las 9 correctness properties definidas en design.md usando hypothesis
- **Performance**: El filtro de dataset debe ejecutar en <50ms según Requirement 10.3
- **Fixture realista**: Los 88 usuarios ficticios deben tener nombres y emails argentinos realistas para simular un entorno de producción
- **Roles variados**: Asegurar que cada uno de los 7 roles está asignado al menos a un usuario Usuario IC para testing completo
- **Fuera de alcance**: La integración con n8n se implementa en `home-chat-orchestrator-contract`, aquí solo se documenta el contrato
- **Fuera de alcance**: La implementación del agente RAG que consume DatasetFilter se implementa en `agente-rag-historial-mails`

## Task Dependency Graph

**Nota:** El siguiente grafo de dependencias con waves está incluido solo como referencia técnica para visualizar qué tareas podrían ejecutarse en paralelo en un entorno automatizado. Sin embargo, la implementación real de este spec se ejecuta **serializada**: una sub-tarea por sesión de Claude Code, en orden (1.1 → 2.1 → 2.2 → 2.3 → 2.4 → 3.1 → 3.2 → 3.3 → ... → 12.1 → 13). No se ejecuta nada en paralelo.

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["2.1", "2.3"] },
    { "id": 2, "tasks": ["2.2", "2.4", "3.1"] },
    { "id": 3, "tasks": ["3.2"] },
    { "id": 4, "tasks": ["3.3"] },
    { "id": 5, "tasks": ["5.1"] },
    { "id": 6, "tasks": ["5.2", "5.3", "5.4"] },
    { "id": 7, "tasks": ["7.1"] },
    { "id": 8, "tasks": ["7.2", "8.1"] },
    { "id": 9, "tasks": ["8.2", "8.3"] },
    { "id": 10, "tasks": ["10.1"] },
    { "id": 11, "tasks": ["10.2", "10.3", "11.1"] },
    { "id": 12, "tasks": ["12.1"] }
  ]
}
```
