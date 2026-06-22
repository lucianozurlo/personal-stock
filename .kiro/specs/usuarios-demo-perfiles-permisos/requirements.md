# Requirements Document

## Introduction

Este spec define el sistema de usuarios demo, perfiles y permisos para Personal Stock MVP 1. El sistema debe crear una base demo de 100 usuarios que incluya 12 usuarios específicos de prueba, implementar 5 perfiles de usuario con permisos diferenciados, asignar roles a usuarios del perfil Usuario IC, y aplicar restricciones de acceso al dataset histórico de mails según perfil.

El dataset histórico existe en `mails/output/relevamiento_enriquecido.json` con la estructura documentada en `ESTRUCTURA_DATASET.md`. Los templates `login.html` y `home.html` ya existen en `./templates`. El proyecto Django vive en `./app`.

## Glossary

- **User_System**: El sistema de gestión de usuarios de Personal Stock
- **Profile**: Categoría de usuario que determina permisos y acceso (Administrador, Usuario IC, Heavy user, Macro, Usuario)
- **Role**: Función específica asignada a usuarios del perfil Usuario IC (Diseñador, Desarrollador, Redactor, Productor, Gerente Cultura, Gerente IC, Especialista)
- **Dataset_Filter**: Mecanismo que aplica restricciones de acceso al dataset histórico según perfil
- **Demo_Base**: Conjunto de 100 usuarios ficticios para pruebas y validación del sistema
- **Test_User**: Usuario específico predefinido con nombre, perfil, rol y email identificados en el brief
- **RAG_System**: Sistema de consulta sobre el dataset histórico de mails (Retrieval-Augmented Generation)
- **Historical_Dataset**: Archivo `mails/output/relevamiento_enriquecido.json` con ~5.300 comunicaciones internas
- **Recipient_Field**: Campo `destinatario` en el dataset que identifica la audiencia de cada comunicación
- **Restricted_Content**: Registros del dataset con destinatario que contiene "macro", "macroestructura", "líderes" o "lideres"

## Requirements

### Requirement 1: Crear Base Demo de 100 Usuarios

**User Story:** Como desarrollador, quiero una base demo de 100 usuarios, para poder probar segmentación, audiencias y permisos sin usar datos reales.

#### Acceptance Criteria

1. THE User_System SHALL create exactly 100 user records in the demo database
2. THE User_System SHALL distribute users across all 5 profiles (Administrador, Usuario IC, Heavy user, Macro, Usuario)
3. THE User_System SHALL include at least 15 users with profile Usuario IC for testing role assignments
4. THE User_System SHALL include at least 30 users with profile Usuario for testing restricted access
5. THE User_System SHALL generate realistic Argentine first names, last names, and email addresses for demo users
6. THE User_System SHALL avoid duplicate email addresses within the demo base

### Requirement 2: Incluir 12 Usuarios Específicos de Prueba

**User Story:** Como desarrollador, quiero que los 12 usuarios de prueba definidos en el brief estén incluidos en la base demo, para poder validar perfiles, roles y permisos con identidades conocidas.

#### Acceptance Criteria

1. THE User_System SHALL include Luciano Zurlo with profile Administrador, roles Diseñador and Desarrollador, and email comustock.ci@gmail.com
2. THE User_System SHALL include Diego Ferrari with profile Usuario IC, role Redactor, and email comustock.uci1@gmail.com
3. THE User_System SHALL include Sara Astudillo with profile Usuario IC, role Diseñador, and email comustock.uci2@gmail.com
4. THE User_System SHALL include Martín Caso with profile Usuario IC, role Productor, and email comustock.uci3@gmail.com
5. THE User_System SHALL include Sebastián Álvarez Hincaipié with profile Usuario IC, role Productor, and email comustock.uci4@gmail.com
6. THE User_System SHALL include Emiliano Zabuski with profile Usuario IC, role Redactor, and email comustock.uci5@gmail.com
7. THE User_System SHALL include Jonathan Ferraro with profile Usuario IC, role Gerente Cultura, and email comustock.g2@gmail.com
8. THE User_System SHALL include Luciana Dau with profile Usuario IC, role Gerente IC, and email comustock.g1@gmail.com
9. THE User_System SHALL include Pablo Giglio with profile Usuario and email comustock.u1@gmail.com
10. THE User_System SHALL include Javier Vulich with profile Usuario and email comustock.u2@gmail.com
11. THE User_System SHALL include Sebastián Marzico with profile Usuario and email comustock.u3@gmail.com
12. THE User_System SHALL include Santiago Gugger with profile Usuario and email comustock.u4@gmail.com

### Requirement 3: Implementar 5 Perfiles de Usuario

**User Story:** Como usuario del sistema, quiero tener un perfil asignado, para que el sistema determine qué permisos y contenidos puedo acceder.

#### Acceptance Criteria

1. THE User_System SHALL support exactly 5 profiles: Administrador, Usuario IC, Heavy user, Macro, and Usuario
2. THE User_System SHALL assign exactly one profile to each user
3. THE User_System SHALL store the profile assignment persistently in the database
4. THE User_System SHALL expose the current user's profile to the authentication system
5. THE User_System SHALL expose the current user's profile to the RAG_System for permission filtering

### Requirement 4: Asignar Roles a Usuarios del Perfil Usuario IC

**User Story:** Como usuario con perfil Usuario IC, quiero tener uno o más roles asignados, para reflejar mi función dentro del equipo de Comunicación Interna.

#### Acceptance Criteria

1. WHERE a user has profile Usuario IC, THE User_System SHALL allow assignment of zero or more roles from the set: Diseñador, Desarrollador, Redactor, Productor, Gerente Cultura, Gerente IC, Especialista
2. WHERE a user does not have profile Usuario IC, THE User_System SHALL not assign any role
3. THE User_System SHALL store role assignments persistently in the database
4. THE User_System SHALL support multiple roles for a single Usuario IC user
5. THE User_System SHALL expose the current user's roles to the orquestador for workflow assignment

### Requirement 5: Filtrar Dataset Histórico por Perfil

**User Story:** Como usuario con perfil Usuario, no quiero acceder a comunicaciones restringidas dirigidas a macro, macroestructura o líderes, para respetar la confidencialidad de información de nivel directivo.

#### Acceptance Criteria

1. WHEN the Recipient_Field of a Historical_Dataset record contains the substring "macro", THE Dataset_Filter SHALL exclude that record from results for users with profile Usuario
2. WHEN the Recipient_Field of a Historical_Dataset record contains the substring "macroestructura", THE Dataset_Filter SHALL exclude that record from results for users with profile Usuario
3. WHEN the Recipient_Field of a Historical_Dataset record contains the substring "líderes", THE Dataset_Filter SHALL exclude that record from results for users with profile Usuario
4. WHEN the Recipient_Field of a Historical_Dataset record contains the substring "lideres", THE Dataset_Filter SHALL exclude that record from results for users with profile Usuario
5. THE Dataset_Filter SHALL perform substring matching in a case-insensitive manner
6. THE Dataset_Filter SHALL apply the exclusion filter before constructing the RAG_System context
7. WHERE a user has profile Administrador, Usuario IC, Heavy user, or Macro, THE Dataset_Filter SHALL not apply the Recipient_Field substring restriction described in AC1-4
8. THE Dataset_Filter SHALL allow other permission mechanisms to exclude records for any profile, including Usuario, beyond the Recipient_Field restrictions

### Requirement 6: Responder de Forma Segura Ante Contenido Restringido

**User Story:** Como usuario con perfil Usuario, quiero recibir una respuesta clara cuando consulto sobre contenido restringido, para entender que existe información pero no tengo permiso para verla.

#### Acceptance Criteria

1. WHEN the RAG_System identifies Restricted_Content relevant to a user query, AND the user has profile Usuario, THE RAG_System SHALL return the safe response message: "Encontré información relacionada con ese tema, pero pertenece a comunicaciones restringidas para otro perfil de usuario. No tengo permiso para mostrar ese contenido."
2. THE RAG_System SHALL not include any fragment, summary, or contextual information from Restricted_Content in the response to users with profile Usuario
3. THE RAG_System SHALL not cite, paraphrase, or reference the content of Restricted_Content in responses to users with profile Usuario

### Requirement 7: Cargar Usuarios desde CSV o Fixture

**User Story:** Como desarrollador, quiero cargar la base demo de usuarios desde un archivo CSV o fixture, para poder inicializar el sistema de forma repetible y controlada.

#### Acceptance Criteria

1. THE User_System SHALL support loading user data from a CSV file format with columns: first_name, last_name, email, profile, roles, cargo, es_focus, areas_focus, es_aprobador_default, puede_aprobar, avatar_url, memoria_habilitada
2. THE User_System SHALL support loading user data from a Django fixture file in JSON format
3. WHEN loading user data from CSV or fixture, THE User_System SHALL validate that all 12 Test_User records are present with correct profile, role, and email
4. WHEN loading user data from CSV or fixture, THE User_System SHALL validate that the total user count equals 100
5. IF a user record in the CSV or fixture is missing required fields (nombre, apellido, email, perfil), THEN THE User_System SHALL reject the entire load operation
6. WHEN rejecting a load operation due to validation failure, THE User_System SHALL attempt to return a descriptive error message, but SHALL complete the rejection even if error message generation fails

### Requirement 8: Almacenar Campos de Usuario Según Brief

**User Story:** Como sistema, quiero almacenar todos los campos de usuario sugeridos en el brief, para soportar funcionalidades presentes y futuras de Personal Stock.

#### Acceptance Criteria

1. THE User_System SHALL store the following fields for each user: nombre, apellido, email, perfil, roles, cargo, es_focus, areas_focus, es_aprobador_default, puede_aprobar, avatar_url, memoria_habilitada
2. THE User_System SHALL validate that email is unique across all users
3. THE User_System SHALL validate that perfil is one of the 5 valid profiles
4. THE User_System SHALL validate that roles contains only valid role names when profile is Usuario IC
5. THE User_System SHALL default memoria_habilitada to true if not explicitly provided

### Requirement 9: Exponer Perfil y Roles al Sistema de Autenticación

**User Story:** Como orquestador, necesito conocer el perfil y roles del usuario autenticado, para derivar a los agentes correctos y aplicar permisos de forma consistente.

#### Acceptance Criteria

1. WHEN a user successfully authenticates, THE User_System SHALL include the user's profile in the session data
2. WHEN a user successfully authenticates, THE User_System SHALL include the user's roles (if any) in the session data
3. THE User_System SHALL expose profile and roles through a user context object accessible to Django views
4. THE User_System SHALL include profile and roles in the JSON payload sent to the n8n orquestador webhook
5. THE User_System SHALL conform to the contract defined in the spec `home-chat-orchestrator-contract` for the user object structure

### Requirement 10: Permitir Consulta de Permisos en Tiempo Real

**User Story:** Como RAG_System, necesito consultar los permisos del usuario actual en tiempo real, para aplicar el filtro de dataset antes de construir el contexto para el LLM.

#### Acceptance Criteria

1. THE User_System SHALL provide a function or method that accepts a user identifier and returns the user's profile
2. THE Dataset_Filter SHALL call this function before each RAG query to determine if restrictions apply
3. THE Dataset_Filter SHALL execute in less than 50ms for permission lookup and filtering on the complete Historical_Dataset
4. THE Dataset_Filter SHALL cache user permission data for the duration of a single RAG query execution

## Conflicts and Decisions

### Conflict 1: Ubicación del Proyecto Django

**Conflicto detectado:** El brief indica que "el proyecto Django vive en ./app (no en el workspace root)", pero no especifica si `cs-chat-rag` ya contiene una estructura Django existente que deba reutilizarse o extenderse.

**Resolución:** Antes de implementar, inspeccionar `cs-chat-rag` para determinar si ya existe una base Django. Si existe, extender esa base. Si no existe o es Flask/scripts sueltos, crear nueva estructura Django en `./app` siguiendo las reglas de `tech.md` y `structure.md`.

**Documentación:** Esta decisión se documenta aquí y debe reflejarse en `design.md` con la estructura real encontrada.

### Conflict 2: Estructura Exacta del Campo `destinatario` en el Dataset

**Conflicto detectado:** El brief indica filtrar por subcadenas "macro", "macroestructura", "líderes", "lideres" en el campo `destinatario`, pero `ESTRUCTURA_DATASET.md` define ese campo como texto libre con valor ejemplo "FULL COMPAÑÍA". No está claro si el matching debe ser exacto, por palabra completa, o por subcadena.

**Resolución:** Aplicar matching por subcadena case-insensitive, tal como está especificado en Requirement 5. Esto permite detectar variantes como "Macro y líderes", "MACROESTRUCTURA", "Líderes de área", etc.

**Documentación:** Queda documentado en AC 5 de Requirement 5: "THE Dataset_Filter SHALL perform substring matching in a case-insensitive manner".

### Conflict 3: Roles Múltiples para un Usuario

**Conflicto detectado:** El usuario de prueba "Luciano Zurlo" tiene dos roles: "Diseñador; Desarrollador". No está claro si el sistema debe soportar múltiples roles por usuario o si es un caso especial.

**Resolución:** El sistema debe soportar múltiples roles para cualquier usuario con perfil Usuario IC. Esto se documenta en Requirement 4, AC 4: "THE User_System SHALL support multiple roles for a single Usuario IC user".

**Documentación:** La implementación debe usar una relación many-to-many o un campo de lista/array para almacenar múltiples roles por usuario.

### Conflict 4: Distinción entre "Perfil Usuario no ve contenido restringido" y "Perfiles privilegiados ven todo"

**Conflicto detectado:** AC7 de Requirement 5 inicialmente parecía contradecir AC1-4, sugiriendo que perfiles Administrador, Usuario IC, Heavy user y Macro "no aplican ninguna restricción" cuando en realidad el diseño es que solo perfil Usuario tiene esa restricción específica.

**Resolución:** Se clarifica en AC7 y AC8 que los perfiles Administrador, Usuario IC, Heavy user y Macro no tienen la restricción de Recipient_Field (pueden ver comunicaciones dirigidas a macro/macroestructura/líderes), pero pueden tener otras restricciones aplicadas por otros mecanismos del sistema. El perfil Usuario es el único que tiene bloqueado el acceso a comunicaciones con esos destinatarios específicos.

**Documentación:** Queda documentado en AC7: "no apply the Recipient_Field substring restriction" (específico, no dice "ninguna restricción") y AC8 permite explícitamente otros mecanismos de filtrado.

## Notes

- Este spec asume que la estructura del dataset en `mails/output/relevamiento_enriquecido.json` cumple exactamente con lo documentado en `ESTRUCTURA_DATASET.md`. Si hay discrepancias, deben señalarse antes de implementar.
- La generación de usuarios demo debe producir datos realistas pero ficticios. No usar nombres o emails de personas reales fuera de los 12 usuarios de prueba especificados.
- El filtro de permisos sobre el dataset es crítico para seguridad. Debe aplicarse ANTES de construir el contexto del RAG, nunca después.
- Los 88 usuarios adicionales (100 total - 12 específicos) deben distribuirse de forma que permita probar todos los escenarios: permisos restrictivos (Usuario), permisos amplios (Administrador), roles diversos (Usuario IC con distintos roles), etc.
