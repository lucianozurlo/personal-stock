# Devolución: Design Usuarios Demo Perfiles Permisos

**Fecha:** 2026-06-22
**Spec:** usuarios-demo-perfiles-permisos
**Fase:** Design
**Veredicto:** ✅ Aprobado para revisión del usuario (con correcciones aplicadas)

---

## Documento Generado

**Ubicación:** `/Users/luciano/Desktop/PS-edit/.kiro/specs/usuarios-demo-perfiles-permisos/design.md`

**Secciones incluidas:**

1. Introduction (resolución de Conflict 1)
2. Overview (arquitectura + diagramas)
3. Architecture (Custom User Model)
4. Components and Interfaces
5. Data Models
6. Correctness Properties (9 properties)
7. Error Handling
8. Testing Strategy
9. Notes and Limitations
10. Appendix (CSV template)

---

## Decisiones Técnicas Clave

### 1. Resolución del Conflicto 1: Ubicación del Proyecto Django

**Conflicto original (requirements.md):** No estaba claro si cs-chat-rag ya tenía una base Django existente.

**Investigación realizada:**

- Se inspeccionó la carpeta `cs-chat-rag` completa
- Se verificó que es un proyecto independiente con:
  - Frontend: HTML + CSS + JavaScript vanilla
  - Backend: n8n (orquestación de workflows)
  - Persistencia: PostgreSQL 16 (solo memoria conversacional)
  - Servidor web: nginx (Docker)

**Decisión final:**

- **NO existe base Django en cs-chat-rag**
- El sistema de usuarios se implementará **extendiendo la base Django ya creada en `./app`** por el spec `base-django-login-home`
- No se reutiliza nada arquitecturalmente de cs-chat-rag excepto:
  - Inspiración visual (ya migrada a `./templates`)
  - Esquema PostgreSQL de memoria (para spec futuro)
  - Patrón de orquestación n8n (para contrato futuro)

**Impacto:** Esta decisión permite reutilizar el proyecto Django existente en lugar de crear uno nuevo, manteniendo coherencia con el spec `base-django-login-home`.

### 2. Custom User Model: AbstractUser vs Profile Separado

**Opciones evaluadas:**

- **Opción A:** User estándar de Django + tabla Profile separada (1:1)
- **Opción B:** Extender AbstractUser con campos custom

**Decisión:** Opción B (AbstractUser)

**Justificación:**

- Todos los campos en una tabla (mejor performance)
- Compatibilidad nativa con sistema de auth Django
- Integración directa con admin panel
- No requiere joins para acceder a perfil/roles
- Es la práctica recomendada por Django docs

**Trade-off crítico identificado:**

- Este spec corre **después** del spec `base-django-login-home`
- Ya existe un superusuario creado (tarea 9 del spec 1)
- La migración a AbstractUser requiere:
  1. Respaldar datos del superusuario existente
  2. Aplicar migración que reemplaza `auth_user` por `core_user`
  3. Recrear superusuario después de la migración
  4. Validar autenticación correcta

**Corrección aplicada:** Se actualizó la sección Trade-offs en design.md para documentar esta consideración crítica.

### 3. Email como USERNAME_FIELD

**Decisión:** Usar email en lugar de username para autenticación

**Justificación:**

- Simplifica el flujo de login (un solo campo)
- Es práctica común en aplicaciones modernas
- Los 12 usuarios específicos ya están definidos por email en el brief
- Elimina necesidad de generar usernames ficticios

**Implicación:** El modelo User hereda el campo `username` de AbstractUser pero no se usa (email es el identificador único).

### 4. Roles como ManyToMany vs JSONField

**Opciones evaluadas:**

- **Opción A:** Campo JSONField o ArrayField con lista de roles
- **Opción B:** Tabla Role + relación ManyToMany

**Decisión:** Opción B (ManyToMany)

**Justificación:**

- Integridad referencial (Django valida roles válidos)
- Queries eficientes (joins optimizados por Django ORM)
- Facilita agregar metadata a roles (descripción, permisos futuros)
- Soporte nativo en admin panel (widget de selección múltiple)

**Requisito cubierto:** Requirement 4.4 - soporte de múltiples roles para Usuario IC (ej: "Diseñador; Desarrollador" para Luciano Zurlo)

### 5. DatasetFilter como Clase vs Función

**Decisión:** Implementar como clase `DatasetFilter` en lugar de función standalone

**Justificación:**

- Encapsula lógica de filtrado relacionada
- Permite extensión futura (subclases, filtros adicionales)
- Métodos de clase reutilizables desde cualquier componente
- Facilita testing (mock/patch de métodos específicos)

**Ubicación:** `app/core/permissions.py`

**Interfaz pública:**

- `filter_by_profile(user, dataset_records) -> list`
- `is_record_restricted(record, user) -> bool`

### 6. Fixture JSON vs CSV como Formato Principal

**Decisión:** Soportar ambos, con fixture JSON como recomendado

**Justificación:**

- **Fixture JSON:** Nativo de Django, integración con `loaddata`, tipo-safe
- **CSV:** Más fácil de editar manualmente, interoperable con Excel/Google Sheets
- Comando `load_demo_users` acepta ambos con flag `--fixture` o `--csv`

**Generación:** Se incluye template CSV en Appendix con reglas para generar 88 usuarios ficticios.

---

## Estructura del Modelo de Datos

### User Model (core.User)

**Extiende:** `django.contrib.auth.models.AbstractUser`

**Campos propios (12 campos de negocio):**

| Campo                | Tipo              | Constraint           | Default   | Propósito                |
| -------------------- | ----------------- | -------------------- | --------- | ------------------------ |
| email                | EmailField        | UNIQUE, NOT NULL     | -         | USERNAME_FIELD           |
| perfil               | CharField(20)     | CHOICES (5 perfiles) | 'Usuario' | Categoría de permisos    |
| roles                | ManyToMany → Role | -                    | -         | Roles para Usuario IC    |
| cargo                | CharField(100)    | -                    | ''        | Puesto de trabajo        |
| es_focus             | BooleanField      | -                    | False     | Usuario especialista     |
| areas_focus          | CharField(200)    | -                    | ''        | Áreas separadas por coma |
| es_aprobador_default | BooleanField      | -                    | False     | Aprobador automático     |
| puede_aprobar        | BooleanField      | -                    | False     | Permiso de aprobación    |
| avatar_url           | URLField          | -                    | ''        | Path al avatar           |
| memoria_habilitada   | BooleanField      | -                    | True      | Memoria conversacional   |

**Campos heredados de AbstractUser (10 campos estándar):**

- username, password, first_name, last_name
- is_active, is_staff, is_superuser
- date_joined, last_login

**Métodos custom:**

- `has_restricted_access() -> bool` - True si perfil == Usuario
- `can_access_restricted_content() -> bool` - True si perfil privilegiado

**Configuración:**

```python
# settings.py
AUTH_USER_MODEL = 'core.User'
```

### Role Model (core.Role)

**Campos:**

| Campo       | Tipo          | Constraint                | Propósito            |
| ----------- | ------------- | ------------------------- | -------------------- |
| name        | CharField(20) | UNIQUE, CHOICES (7 roles) | Nombre del rol       |
| description | TextField     | -                         | Descripción opcional |

**7 Roles válidos:**

1. Diseñador
2. Desarrollador
3. Redactor
4. Productor
5. Gerente Cultura
6. Gerente IC
7. Especialista

**Relación:** ManyToMany con User (tabla intermedia `core_user_roles`)

### Database Schema

```
┌──────────────────────┐         ┌──────────────────┐
│ core_user            │         │ core_role        │
├──────────────────────┤         ├──────────────────┤
│ id (PK)              │         │ id (PK)          │
│ email (UK)           │         │ name (UK)        │
│ first_name           │         │ description      │
│ last_name            │         └──────────────────┘
│ password                         │
│ perfil (choices)     │         ┌──────────────────────┐
│ cargo                │         │ core_user_roles      │
│ es_focus             ├────────┤├──────────────────────┤
│ areas_focus          │         │ id (PK)              │
│ es_aprobador_default │         │ user_id (FK)         │
│ puede_aprobar        │         │ role_id (FK)         │
│ avatar_url           │         └──────────────────────┘
│ memoria_habilitada   │
│ is_active            │
│ is_staff             │
│ is_superuser         │
│ date_joined          │
│ last_login           │
└──────────────────────┘
```

**Indexes:**

- `email` (automático por UNIQUE)
- `perfil` (consultas frecuentes)
- `es_focus` (filtros comunes)

---

## Componentes Diseñados

### 1. DatasetFilter (core/permissions.py)

**Responsabilidad:** Filtrar registros del dataset histórico según perfil del usuario.

**Algoritmo:**

```python
def filter_by_profile(user, dataset_records):
    # 1. Validar que user tiene perfil
    if not user.perfil:
        raise ValueError("Usuario sin perfil definido")

    # 2. Perfiles privilegiados ven todo
    if user.can_access_restricted_content():
        return dataset_records

    # 3. Perfil Usuario: filtrar por destinatario
    filtered = []
    for record in dataset_records:
        destinatario = record['destinatario'].lower()

        # Excluir si contiene substring restringida
        is_restricted = any(
            substring in destinatario
            for substring in ['macro', 'macroestructura', 'líderes', 'lideres']
        )

        if not is_restricted:
            filtered.append(record)

    return filtered
```

**Performance:** Debe ejecutar en <50ms sobre ~5.300 registros (Requirement 10.3)

**Testing:** Property 5 y Property 6 validan correctness del filtro

### 2. Management Command: load_demo_users

**Ubicación:** `app/core/management/commands/load_demo_users.py`

**Interfaz de comandos:**

```bash
# Cargar desde fixture JSON (recomendado)
python manage.py load_demo_users --fixture fixtures/demo_users.json

# Cargar desde CSV
python manage.py load_demo_users --csv path/to/usuarios_demo.csv

# Validar sin cargar (dry-run)
python manage.py load_demo_users --fixture fixtures/demo_users.json --dry-run
```

**Validaciones obligatorias:**

| Validación                        | Acción si falla                         |
| --------------------------------- | --------------------------------------- |
| Total usuarios == 100             | Rechazar carga, mostrar total detectado |
| 12 usuarios específicos presentes | Rechazar carga, listar faltantes        |
| Emails únicos                     | Rechazar carga, listar duplicados       |
| Campos obligatorios completos     | Rechazar carga, listar faltantes        |
| Perfil válido                     | Rechazar carga, listar inválidos        |
| Roles válidos si Usuario IC       | Rechazar carga, listar inválidos        |

**Manejo de errores:** Rechazo atómico (todo o nada) con mensaje descriptivo.

### 3. Fixture y CSV

**fixtures/demo_users.json:**

- Formato: Django fixture estándar
- Contenido: 100 usuarios (12 específicos + 88 ficticios)
- Roles: Asignados en fixture separado o via señales post_save

**CSV Template (Appendix):**

- Columnas: first_name, last_name, email, perfil, roles, cargo, es_focus, areas_focus, es_aprobador_default, puede_aprobar, avatar_url, memoria_habilitada
- Roles múltiples: Separados por punto y coma (;)
- Booleanos: true/false o 1/0

**Reglas de generación para 88 ficticios:**

- Nombres/apellidos argentinos comunes
- Emails: `demo.user{N}@personalstock.local` (N=13 a 100)
- Distribución perfiles:
  - 3-5 Administrador
  - 15-20 Usuario IC
  - 30-35 Usuario
  - 10-15 Heavy user
  - 10-15 Macro

---

## Correctness Properties (9 propiedades testables)

### Testing con Property-Based Testing (hypothesis)

**Configuración:**

```python
from hypothesis import given, strategies as st, settings

settings.register_profile("usuarios", max_examples=100, deadline=1000)
settings.load_profile("usuarios")
```

### Propiedades Identificadas

| #   | Property                                   | Valida Requirements | Tipo        |
| --- | ------------------------------------------ | ------------------- | ----------- |
| 1   | Email Uniqueness                           | 1.6, 8.2            | UNIVERSAL   |
| 2   | Profile Persistence                        | 3.2, 3.3            | PERSISTENCE |
| 3   | Role Assignment for Usuario IC             | 4.1, 4.3, 4.4       | CONSTRAINT  |
| 4   | Role Restriction for Non-Usuario IC        | 4.2                 | CONSTRAINT  |
| 5   | Dataset Filtering by Restricted Substrings | 5.1-5.5             | LOGIC       |
| 6   | Dataset Access for Privileged Profiles     | 5.7                 | LOGIC       |
| 7   | Profile Validation                         | 8.3                 | VALIDATION  |
| 8   | Invalid Role Rejection                     | 8.4                 | VALIDATION  |
| 9   | CSV Load Rejection on Missing Fields       | 7.5                 | VALIDATION  |

### Distribución de Tests

- **40% Property-Based Testing** (hypothesis) - 100 iterations por property
- **40% Unit Tests** - Validaciones específicas (12 usuarios, distribución, defaults)
- **20% Integration Tests** - Flujos end-to-end (comando, filtro real, performance)

**Cobertura esperada:**

- Line coverage: ≥90% para models.py y permissions.py
- Branch coverage: ≥85% para lógica de filtrado
- Property tests: 100 iterations por property

---

## Consideraciones de Seguridad

### 1. Password Hashing

Django automáticamente hashea passwords con PBKDF2. No se almacenan en claro ni en fixtures.

### 2. Email como Username

El email se expone en URLs del admin panel, pero es aceptable para MVP interno. En producción considerar ofuscar emails en logs.

### 3. Filtro de Dataset: Única Barrera de Seguridad

**CRÍTICO:** El `DatasetFilter` es la **única barrera** entre usuarios con perfil Usuario y contenido restringido.

**Regla obligatoria:** El agente RAG **siempre** debe llamar al filtro antes de construir contexto para el LLM. No debe haber bypass ni caché sin validar permisos.

**Validación:** Property 5 y Property 6 testean exhaustivamente que:

- Perfil Usuario NO ve registros con destinatarios restringidos
- Perfiles privilegiados SÍ ven todos los registros

### 4. Validación de Roles

La validación de que solo Usuario IC puede tener roles debe implementarse como:

1. **Constraint de modelo** (ValidationError en clean())
2. **Señal pre_save** (prevenir bypass)

No debe depender solo de validación de formularios (pueden bypassed).

---

## Limitaciones MVP 1

### 1. Avatares

El campo `avatar_url` existe pero no se usa en MVP 1. Implementación en spec posterior de UI.

### 2. Áreas Focus como String

Campo `areas_focus` almacena áreas separadas por coma. Normalizar a tabla Areas + ManyToMany en spec posterior.

### 3. Caching de Permisos

Requirement 10.4 especifica cache de permisos durante query RAG. Implementación delegada al spec `agente-rag-historial-mails`.

### 4. Respuesta Segura ante Contenido Restringido

Requirement 6 (mensaje del RAG) se implementa en spec del agente RAG, no aquí. Este spec solo provee el filtro.

### 5. Exposición a n8n

Requirement 9 (payload JSON al orquestador) se implementa en spec `home-chat-orchestrator-contract`.

---

## Archivos Generados/Modificados

### Nuevos

1. `/Users/luciano/Desktop/PS-edit/.kiro/specs/usuarios-demo-perfiles-permisos/design.md`
2. `/Users/luciano/Desktop/PS-edit/docs/devoluciones/35-design-usuarios-demo-perfiles-permisos.md` (este archivo)

### Modificados

1. `design.md` - Corrección de Trade-offs sobre orden de ejecución de specs

---

## Correcciones Aplicadas

### Corrección 1: Orden de Ejecución de Specs

**Error original:**

> "Pero: este spec corre **antes** del spec `base-django-login-home`, así que no hay datos existentes"

**Corrección aplicada:**

> "**IMPORTANTE:** Este spec corre **después** del spec `base-django-login-home`, lo que significa que ya existe un superusuario creado (tarea 9 del spec 1). La migración a AbstractUser requiere:
>
> 1. Respaldar datos del superusuario existente (email, password hash)
> 2. Aplicar migración que reemplaza tabla `auth_user` por `core_user`
> 3. Recrear superusuario con `createsuperuser` o migración de datos
> 4. Validar que el superusuario puede autenticarse correctamente"

**Impacto:** Esta corrección es crítica porque afecta el plan de implementación en tasks.md. La primera tarea debe incluir pasos para preservar el superusuario existente.

---

## Diagramas Incluidos

### 1. Arquitectura del Sistema de Usuarios

Diagrama de componentes mostrando:

- Browser → Django Application
- Custom User Model
- Dataset Filter
- Management Command
- SQLite DB

### 2. Flujo de Filtrado de Dataset

Sequence diagram (Mermaid) mostrando:

- RAG → User Model (obtener perfil)
- RAG → Dataset (cargar JSON)
- RAG → DatasetFilter (aplicar filtro)
- DatasetFilter → RAG (registros permitidos)

### 3. Database Schema

ER diagram (Mermaid) mostrando:

- core_user (User model)
- core_role (Role model)
- core_user_roles (tabla intermedia ManyToMany)

---

## Próximos Pasos

1. ✅ **Requirements aprobados**
2. ✅ **Design completado**
3. ✅ **Corrección de orden de specs aplicada**
4. ✅ **Devolución de design generada**
5. ⏳ **Esperando aprobación del usuario**
6. ⏸️ **NO generar tasks.md todavía** (esperando confirmación)

---

## Veredicto Final

✅ **Design completado y corregido**
✅ **Sin errores de diagnóstico**
✅ **Decisiones técnicas documentadas**
✅ **Correcciones críticas aplicadas**

El diseño técnico está completo y listo para implementación. Incluye:

- Custom User Model con 5 perfiles y 7 roles
- DatasetFilter reutilizable con 9 correctness properties
- Management command con validaciones estrictas
- Testing strategy balanceado (PBT + unit + integration)
- Consideración crítica sobre superusuario existente

**⚠️ Corrección crítica aplicada:** Documentado que este spec corre **después** de base-django-login-home y que el superusuario existente debe preservarse durante la migración.

**Estado:** Esperando aprobación del usuario antes de generar tasks.md.
