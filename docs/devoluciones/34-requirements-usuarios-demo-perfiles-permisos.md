# Devolución: Requirements Usuarios Demo Perfiles Permisos

**Fecha:** 2026-06-22
**Spec:** usuarios-demo-perfiles-permisos
**Fase:** Requirements
**Veredicto:** ✅ Aprobado para revisión del usuario

---

## Documentos Generados

### 1. `.config.kiro`

**Ubicación:** `/Users/luciano/Desktop/PS-edit/.kiro/specs/usuarios-demo-perfiles-permisos/.config.kiro`

**Contenido:**

```json
{
  "specId": "e3bbeb52-6222-405d-99bd-6634cb092352",
  "workflowType": "requirements-first",
  "specType": "feature"
}
```

**Propósito:** Archivo de configuración del spec que identifica el tipo de workflow (requirements-first) y el tipo de spec (feature).

---

### 2. `requirements.md`

**Ubicación:** `/Users/luciano/Desktop/PS-edit/.kiro/specs/usuarios-demo-perfiles-permisos/requirements.md`

**Estructura del documento:**

- **Introduction:** Contexto del spec, alcance MVP 1, ubicación de archivos fuente
- **Glossary:** 11 términos clave definidos (User_System, Profile, Role, Dataset_Filter, etc.)
- **Requirements:** 10 requisitos en formato EARS con 56 criterios de aceptación totales
- **Conflicts and Decisions:** 4 conflictos detectados y resueltos
- **Notes:** Consideraciones de implementación y seguridad

---

## Requisitos Documentados

### Requirement 1: Crear Base Demo de 100 Usuarios

- 6 criterios de aceptación
- Distribución entre los 5 perfiles
- Generación de datos realistas argentinos
- Validación de unicidad de emails

### Requirement 2: Incluir 12 Usuarios Específicos de Prueba

- 12 criterios de aceptación (uno por cada usuario)
- Nombres, perfiles, roles y emails exactos del brief
- Incluye: Luciano Zurlo (Administrador), Diego Ferrari (Usuario IC/Redactor), Sara Astudillo (Usuario IC/Diseñador), etc.

### Requirement 3: Implementar 5 Perfiles de Usuario

- 5 criterios de aceptación
- Perfiles: Administrador, Usuario IC, Heavy user, Macro, Usuario
- Exposición a sistema de autenticación y RAG

### Requirement 4: Asignar Roles a Usuarios del Perfil Usuario IC

- 5 criterios de aceptación
- 7 roles válidos: Diseñador, Desarrollador, Redactor, Productor, Gerente Cultura, Gerente IC, Especialista
- Soporte de roles múltiples (ej: Luciano Zurlo = Diseñador + Desarrollador)
- Restricción: solo usuarios con perfil Usuario IC pueden tener roles

### Requirement 5: Filtrar Dataset Histórico por Perfil

- 8 criterios de aceptación
- **Regla crítica:** perfil Usuario NO accede a registros con destinatario que contenga "macro", "macroestructura", "líderes" o "lideres"
- Matching case-insensitive por subcadena
- Filtro aplicado ANTES de construir contexto RAG
- Otros perfiles (Administrador, Usuario IC, Heavy user, Macro) NO tienen esta restricción

### Requirement 6: Responder de Forma Segura Ante Contenido Restringido

- 3 criterios de aceptación
- Mensaje predefinido: "Encontré información relacionada con ese tema, pero pertenece a comunicaciones restringidas para otro perfil de usuario. No tengo permiso para mostrar ese contenido."
- Sin fragmentos, resúmenes ni contexto de contenido restringido en la respuesta

### Requirement 7: Cargar Usuarios desde CSV o Fixture

- 6 criterios de aceptación
- Formato CSV con columnas específicas del brief
- Formato Django fixture en JSON
- Validación de 12 usuarios de prueba y total de 100
- Rechazo de carga completa si falta algún campo requerido

### Requirement 8: Almacenar Campos de Usuario Según Brief

- 5 criterios de aceptación
- Campos: nombre, apellido, email, perfil, roles, cargo, es_focus, areas_focus, es_aprobador_default, puede_aprobar, avatar_url, memoria_habilitada
- Validaciones de unicidad y valores válidos
- Default memoria_habilitada = true

### Requirement 9: Exponer Perfil y Roles al Sistema de Autenticación

- 5 criterios de aceptación
- Perfil y roles en session data
- Accesible a vistas Django
- Incluido en payload JSON al webhook de n8n
- Conformidad con contrato `home-chat-orchestrator-contract`

### Requirement 10: Permitir Consulta de Permisos en Tiempo Real

- 4 criterios de aceptación
- Función de lookup de permisos por user identifier
- Ejecución en <50ms sobre dataset completo
- Cache de permisos durante ejecución de query RAG

---

## Conflictos Detectados y Resueltos

### Conflicto 1: Ubicación del Proyecto Django

**Detectado:** Brief indica "./app" pero no especifica si `cs-chat-rag` ya tiene Django.
**Resolución:** Inspeccionar `cs-chat-rag` primero. Si existe Django, extender; si no, crear en `./app`.
**Estado:** Documentado para resolución en fase de diseño.

### Conflicto 2: Estructura Exacta del Campo `destinatario`

**Detectado:** No claro si matching es exacto, por palabra o por subcadena.
**Resolución:** Matching por subcadena case-insensitive (detecta "Macro y líderes", "MACROESTRUCTURA", etc.).
**Estado:** ✅ Resuelto y documentado en AC5 de Requirement 5.

### Conflicto 3: Roles Múltiples para un Usuario

**Detectado:** Luciano Zurlo tiene "Diseñador; Desarrollador" — ¿es caso especial o regla general?
**Resolución:** Soporte general de múltiples roles para cualquier Usuario IC.
**Estado:** ✅ Resuelto y documentado en Requirement 4, AC4.

### Conflicto 4: Distinción entre Perfiles y Restricciones

**Detectado:** Posible confusión entre "Usuario no ve restringido" vs "otros perfiles ven todo".
**Resolución:** Solo perfil Usuario tiene restricción de Recipient_Field. Otros perfiles no tienen esa restricción específica (pueden tener otras).
**Estado:** ✅ Clarificado en AC7 y AC8 de Requirement 5.

---

## Decisiones Aplicadas

### 1. Formato EARS Estricto

Todos los criterios de aceptación usan formato EARS:

- WHERE (condición de contexto)
- WHILE (condición de duración)
- WHEN (trigger o evento)
- IF ... THEN (condicional)
- THE [sistema] SHALL [acción obligatoria]

### 2. Filtro de Dataset ANTES de Contexto RAG

Decisión crítica de seguridad: el filtro de permisos se aplica ANTES de armar el contexto para el LLM, no después. Esto previene que contenido restringido llegue al prompt del modelo.

### 3. Matching Case-Insensitive por Subcadena

Para cubrir todas las variantes posibles de "macro", "macroestructura", "líderes", "lideres" en el campo destinatario (MACRO, Líderes de área, macro y líderes, etc.).

### 4. Usuarios Demo Realistas pero Ficticios

Los 88 usuarios adicionales (100 total - 12 específicos) deben tener nombres y emails realistas argentinos pero completamente ficticios. No usar datos de personas reales.

### 5. Soporte de Múltiples Roles

El modelo de datos debe soportar many-to-many o array para roles, permitiendo casos como "Diseñador + Desarrollador" para un mismo usuario IC.

### 6. Validación de Dataset contra ESTRUCTURA_DATASET.md

Se verificó que el campo `destinatario` existe en el schema documentado y que hay registros reales con "LÍDERES", "Líderes", "MACROESTRUCTURA" que deben filtrarse.

---

## Análisis de Requirements Ejecutado

Se ejecutó el análisis de requirements con la herramienta Kiro Reasoning Service. Resultados:

### Auto-Resoluciones Aplicadas (3)

1. **Definición de "memoria_habilitada":** Campo booleano que controla si el sistema almacena historial de conversación del usuario.
2. **Definición de "areas_focus":** Lista de áreas temáticas o departamentos que un usuario Focus puede aprobar o supervisar.
3. **Definición de "puede_aprobar":** Capacidad de un usuario para aprobar comunicaciones o proyectos en workflows.

### Respuestas del Usuario Incorporadas (3)

1. **Roles vacíos para Usuario IC:** Usuario IC puede tener cero roles (caso válido durante onboarding o transición).
2. **Performance del filtro de dataset:** Debe ejecutar en <50ms sobre dataset completo (~5.300 registros).
3. **Formato de respuesta ante contenido restringido:** Usar exactamente el mensaje del brief sin variaciones.

---

## Verificación de Formato

✅ **Sin errores de diagnóstico:** El documento `requirements.md` fue validado con `getDiagnostics` y no reportó errores de formato.

---

## Archivos Fuente Consultados

1. `/Users/luciano/Desktop/PS-edit/brief-personal-stock.md` — Brief completo del proyecto
2. `/Users/luciano/Desktop/PS-edit/ESTRUCTURA_DATASET.md` — Schema del dataset histórico
3. `/Users/luciano/Desktop/PS-edit/brand_key_voz_tono_personal.md` — Manual de voz y tono (referencia)
4. `/Users/luciano/Desktop/PS-edit/.kiro/steering/product.md` — Reglas de producto
5. `/Users/luciano/Desktop/PS-edit/.kiro/steering/tech.md` — Stack y restricciones técnicas
6. `/Users/luciano/Desktop/PS-edit/.kiro/steering/structure.md` — Estructura del proyecto
7. `/Users/luciano/Desktop/PS-edit/.kiro/steering/security-permissions.md` — Seguridad y permisos
8. `/Users/luciano/Desktop/PS-edit/.kiro/steering/rules.md` — Reglas de proceso

---

## Fase 2: Design.md Completado

**Archivo generado:** `/Users/luciano/Desktop/PS-edit/.kiro/specs/usuarios-demo-perfiles-permisos/design.md`

### Resolución del Conflicto 1

**Conflicto:** Ubicación del proyecto Django (cs-chat-rag vs ./app)

**Inspección realizada:** Se analizó cs-chat-rag y se confirmó que:

- Es un proyecto independiente (HTML + n8n + PostgreSQL)
- NO tiene base Django existente
- Usa nginx para servir frontend estático

**Decisión final:** Extender la base Django ya creada en `./app` por el spec `base-django-login-home`. No se reutiliza nada arquitecturalmente de cs-chat-rag.

### Componentes Diseñados

#### 1. Custom User Model

- Extiende `AbstractUser` de Django
- Email como USERNAME_FIELD (único)
- 5 perfiles: Administrador, Usuario IC, Heavy user, Macro, Usuario
- ManyToMany a Role para usuarios IC
- 12 campos de negocio del brief
- Métodos helpers: `has_restricted_access()`, `can_access_restricted_content()`

#### 2. Role Model

- 7 roles válidos para Usuario IC
- Choices constraint en Django
- Relación ManyToMany con User

#### 3. DatasetFilter Class

- Ubicación: `app/core/permissions.py`
- Método principal: `filter_by_profile(user, dataset_records)`
- Filtra por subcadenas case-insensitive en campo `destinatario`
- Restricciones: "macro", "macroestructura", "líderes", "lideres"
- Solo aplica a perfil Usuario

#### 4. Management Command: load_demo_users

- Soporta CSV y fixture JSON
- Validaciones estrictas: 100 usuarios, 12 específicos, campos obligatorios
- Rechazo atómico si falta alguna validación
- Flags: `--fixture`, `--csv`, `--dry-run`

#### 5. Fixture JSON + CSV Template

- `fixtures/demo_users.json` con 100 usuarios
- Template CSV en appendix con reglas de generación
- 12 específicos + 88 ficticios con nombres argentinos

### Decisiones de Arquitectura

1. **AbstractUser vs User + Profile separado:** Se eligió AbstractUser para simplificar y mantener compatibilidad con sistema de auth Django.

2. **Email como username:** Simplifica login (un solo campo) y es práctica común en apps modernas.

3. **ManyToMany para roles:** Permite roles múltiples como "Diseñador; Desarrollador" para Luciano Zurlo.

4. **DatasetFilter como clase separada:** Reutilizable desde cualquier componente (RAG, API, views).

5. **Áreas como string CSV:** Para MVP 1 es texto separado por comas. En spec posterior se normalizará a tabla.

### Correctness Properties Identificadas

Se identificaron **9 properties testables** con Property-Based Testing:

1. **Email Uniqueness** - Para cualquier conjunto de usuarios, emails únicos
2. **Profile Persistence** - Perfil persiste correctamente al guardar/recargar
3. **Role Assignment for Usuario IC** - Múltiples roles permitidos solo para Usuario IC
4. **Role Restriction for Non-Usuario IC** - Otros perfiles NO tienen roles
5. **Dataset Filtering by Restricted Substrings** - Filtro excluye registros restringidos
6. **Dataset Access for Privileged Profiles** - Perfiles privilegiados ven todo
7. **Profile Validation** - Django rechaza perfiles inválidos
8. **Invalid Role Rejection** - Django rechaza roles inválidos
9. **CSV Load Rejection on Missing Fields** - Comando rechaza carga incompleta

### Testing Strategy

- **40% Property-Based Testing** (hypothesis) - 100 iterations por property
- **40% Unit Tests** - Validaciones específicas (12 usuarios, distribución, defaults)
- **20% Integration Tests** - Flujos end-to-end (comando, filtro con dataset real)
- **Performance test:** Filtro debe ejecutar en <50ms sobre ~5.300 registros

### Diagramas Incluidos

1. **Arquitectura del Sistema de Usuarios** (componentes + flujo)
2. **Flujo de Filtrado de Dataset** (sequence diagram Mermaid)
3. **Database Schema** (ER diagram Mermaid)

### Security Considerations

- Password hashing automático (PBKDF2)
- Email expuesto en admin (aceptable para MVP interno)
- **Filtro de dataset es la única barrera** - crítico que RAG siempre lo use
- Validación de roles debe ser constraint de modelo, no solo formulario

### Limitaciones MVP 1 Documentadas

1. Avatar URL existe pero no se usa (spec posterior de UI)
2. Áreas focus como texto (normalizar en spec posterior)
3. Caching de permisos delegado al spec del agente RAG
4. Respuesta segura implementada en spec del agente RAG, no aquí
5. Exposición a n8n implementada en spec del contrato orquestador

---

## Próximos Pasos

1. ~~**Revisión del usuario:** requirements.md~~ ✅ **Completado**
2. ~~**Resolución de Conflicto 1:** Inspeccionar cs-chat-rag~~ ✅ **Resuelto (no tiene Django)**
3. ~~**Generación de design.md:**~~ ✅ **Completado**
4. **Generación de tasks.md:** Crear el plan de tareas de implementación dividido en sub-tareas verificables
5. **Validación del spec completo:** Revisión final del usuario antes de implementación

---

## Veredicto Final

✅ **Requirements aprobados**
✅ **Design completado y validado**
✅ **Sin errores de diagnóstico**

El spec está listo para la fase de tasks. El sistema de usuarios demo, perfiles y permisos está completamente diseñado con:

- Modelo de datos detallado (User + Role)
- Componente de filtrado reutilizable (DatasetFilter)
- Comando de carga con validaciones estrictas
- 9 correctness properties identificadas
- Testing strategy balanceado (PBT + unit + integration)
- Security y limitaciones documentadas

**Siguiente paso:** Generar tasks.md con el plan de implementación.
