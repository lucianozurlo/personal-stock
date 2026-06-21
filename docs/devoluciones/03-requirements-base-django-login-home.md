# Devolución: Requirements base-django-login-home

## Qué se generó

Se creó el spec `base-django-login-home` con el documento **requirements.md** que define 10 requirements con 50 acceptance criteria en formato EARS estricto.

**Archivos creados:**

- `.kiro/specs/base-django-login-home/.config.kiro` (configuración del spec)
- `.kiro/specs/base-django-login-home/requirements.md`

---

## Alcance cubierto

El spec cubre la creación de la base Django para Personal Stock y la integración de los templates de login y home existentes:

### Requirement 1: Bootstrap del proyecto Django

- Crear proyecto Django en `./app/` con `django-admin startproject config .`
- Instalar `dj-database-url` en requirements.txt con versión pinada
- Cablear `DATABASE_URL` en settings.py usando `dj_database_url.parse()`
- Cablear `DJANGO_SECRET_KEY` en settings.py
- Configurar INSTALLED_APPS con apps por defecto
- Validar que `python manage.py migrate` crea db.sqlite3

### Requirement 2: Configuración de templates fuente

- Configurar `TEMPLATES[0]['DIRS']` con `BASE_DIR.parent / 'templates'`
- Validar que Django encuentra templates/home.html y templates/login.html
- Mantener templates fuente en ./templates (NO copiarlos a ./app)

### Requirement 3: Configuración de archivos estáticos

- Configurar `STATICFILES_DIRS` con rutas a templates/css/, templates/js/, templates/img/
- Validar que `collectstatic` copia correctamente los assets
- Validar que `{% static %}` resuelve rutas correctamente

### Requirement 4: Sistema de autenticación básico

- Habilitar SessionMiddleware y AuthenticationMiddleware
- Redirigir usuarios no autenticados de `/` a `/login/`
- Autenticar con `authenticate()` y `login()` de Django
- Crear sesión persistente tras login exitoso
- Permitir acceso a `/` para usuarios autenticados
- Implementar logout que destruye la sesión

### Requirement 5: Integración del template login.html

- Crear vista `login_view` que renderiza login.html
- Configurar ruta `/login/` en urls.py
- Validar credenciales contra Django auth usando email como username
- Mostrar mensaje de error si credenciales incorrectas
- Redirigir a `/` tras login exitoso

### Requirement 6: Integración del template home.html

- Crear vista `home_view` con decorador `@login_required`
- Renderizar home.html con usuario logueado en contexto
- Configurar ruta `/` en urls.py
- Validar que usuarios no autenticados son redirigidos a login

### Requirement 7: Reemplazo de usuario hardcodeado en home.html

- Pasar objeto `user` en contexto del template
- Reemplazar "Benja" por `{{ user.first_name }}` en welcomeTitle
- Usar `{{ user.username }}` como fallback si first_name vacío

### Requirement 8: Reemplazo de usuario hardcodeado en app.js

- Inyectar variable JavaScript `window.PS_USER` con firstName y username
- Reemplazar todas las ocurrencias de "Benja" en app.js por referencia dinámica
- Modificar RANDOM_GREETINGS para usar window.PS_USER.firstName
- Actualizar getTimeBasedGreeting() para usar usuario dinámico

### Requirement 9: Sesión persistente

- Crear entrada en tabla django_session tras autenticación
- Reconocer sesión existente mediante cookie sessionid
- Mantener sesión tras recarga de página
- Implementar checkbox "Recordarme" (sesión persiste tras cerrar navegador)
- Destruir sesión si checkbox no marcado al cerrar navegador
- Redirigir a login si sesión expira o es inválida

### Requirement 10: Validación de cableo de variables de entorno

- Verificar DATABASE_URL cableada en settings.py
- Verificar DJANGO_SECRET_KEY cableada en settings.py
- Validar que `python manage.py check` completa sin warnings
- Fallar con mensaje claro si DATABASE_URL no definida
- Fallar con mensaje claro si DJANGO_SECRET_KEY no definida

---

## Decisiones aplicadas

### Decisión 1: cs-chat-rag NO es base Django reutilizable

**Origen:** Inventario del workspace y resumen proyecto previo (bot).md

**Hallazgo:** cs-chat-rag es un proyecto independiente con stack:

- Frontend: HTML + CSS + JS vanilla
- Orquestación: n8n
- RAG: JSONL servido como estático
- Memoria: PostgreSQL 16
- Web server: nginx (Docker)
- LLM: Gemini 2.5 Flash + Groq fallback

**Decisión aplicada:**

- Crear ./app Django desde cero (NO intentar convertir cs-chat-rag)
- Solo reutilizar: schema PostgreSQL de memoria conversacional (spec futuro), patrón de orquestación n8n (spec futuro), e inspiración UI de templates
- NO importar cs-chat-rag como módulo Python (no es código Python)

**Impacto:** Requirements 1-10 asumen creación desde cero con `django-admin startproject`.

### Decisión 2: templates/home.html ya existe (NO renombrar)

**Origen:** Inspección de estructura del workspace

**Hallazgo:**

```
templates/
  home.html  ← ya existe
  login.html ← ya existe
  css/
  js/
  img/
```

**Decisión aplicada:**

- NO hay tarea de renombrado de index.html → home.html (el archivo ya se llama home.html)
- Todas las referencias en requirements apuntan directamente a home.html

**Impacto:** Requirements 2, 6 y 7 usan "home.html" sin mención a renombrado.

### Decisión 3: Mantener templates fuente en ./templates (raíz del workspace)

**Origen:** tech.md

**Regla citada:**

> "Mantener templates fuente en ./templates (raíz del workspace, NO dentro de ./app) y conectarlos por configuración de Django: agregar la carpeta a TEMPLATES[0]['DIRS'] en settings.py usando una ruta absoluta vía BASE_DIR.parent"

**Decisión aplicada:**

- Configurar `TEMPLATES[0]['DIRS']` con `BASE_DIR.parent / 'templates'`
- NO copiar templates a ./app/templates/
- Django consume directamente desde ./templates

**Impacto:** Requirement 2 valida que Django encuentra templates en raíz del workspace.

### Decisión 4: Cableo explícito de DATABASE_URL con dj-database-url

**Origen:** tech.md

**Regla citada:**

> "`.env.example` declara `DATABASE_URL`. La tarea que primero la usa (normalmente la tarea 1.1 de `base-django-login-home`, el bootstrap) debe instalar `dj-database-url` y cablearla en `settings.py`"

**Decisión aplicada:**

- Requirement 1 incluye instalación de dj-database-url en requirements.txt
- Requirement 1 incluye cableo en settings.py: `DATABASES['default'] = dj_database_url.parse(os.environ.get('DATABASE_URL'))`
- Requirement 10 valida que la variable no queda declarada sin uso

**Impacto:** Ninguna tarea se considera completa si declara variable de entorno sin cableo real.

### Decisión 5: Reemplazo de "Benja" hardcodeado

**Origen:** brief-personal-stock.md sección 12 + spec maestro decisión #4

**Hallazgo:**

- "Benja" aparece hardcodeado en:
  - `templates/home.html`: `<span id="welcomeTitle">Hola, Benja.</span>`
  - `templates/js/app.js`: array `RANDOM_GREETINGS` con "Hola Benja!"

**Decisión aplicada:**

- Requirement 7: reemplazar en home.html por `{{ user.first_name }}`
- Requirement 8: inyectar `window.PS_USER` e interpolar firstName en app.js
- Solo tocar templates/ y ./app/ (NO tocar cs-chat-rag/)

**Impacto:** Requirements 7 y 8 cubren parametrización completa del usuario.

### Decisión 6: Estructura objetivo del proyecto

**Origen:** structure.md

**Estructura validada:**

```
~/Desktop/PS-edit/
  .kiro/
    steering/
    specs/
  .claude/
  CLAUDE.md
  app/                    ← crear desde cero
    manage.py
    config/
    core/
  templates/              ← mantener como fuente
    home.html
    login.html
    css/
    js/
    img/
  mails/
  cs-chat-rag/           ← NO tocar, solo inspiración
  comustock-base/
```

**Decisión aplicada:**

- ./app se crea desde cero
- templates/ permanece en raíz del workspace
- cs-chat-rag/ no se modifica

**Impacto:** Requirements 1-3 configuran Django para consumir templates desde raíz.

---

## Formato EARS aplicado

Todos los acceptance criteria siguen patrones EARS estrictos:

### Patrones utilizados:

- **WHEN...SHALL**: Para condiciones específicas
  - Ejemplo: "WHEN un usuario no autenticado intenta acceder a la ruta `/` (home), THE Django_App SHALL redirigir al usuario a `/login/`"

- **THE...SHALL**: Para comportamiento obligatorio sin condición previa
  - Ejemplo: "THE Django_App SHALL incluir `dj-database-url` en `requirements.txt` con versión pinada"

- **FOR ALL...SHALL**: Para iteración sobre colecciones
  - Ejemplo: "FOR ALL funciones en `app.js` que referencian "Benja", THE Static_Assets SHALL reemplazar el hardcoded string por la variable dinámica"

- **WHERE...SHALL**: Para definir relaciones o ubicaciones
  - Ejemplo: "THE Django_App SHALL renderizar el template `home.html` usando `render(request, 'home.html', context)` WHERE `context` incluye el usuario logueado"

### Validaciones aplicadas:

✅ Sin pronombres (yo, tú, nosotros)
✅ Sin términos vagos (fácil, rápido, flexible)
✅ Sin escape clauses (si es posible, idealmente)
✅ Todos los términos técnicos definidos en Glossary
✅ Criterios medibles y testables

---

## Conflictos detectados y resoluciones

### Conflicto 1: Brief menciona "index.html" pero archivo se llama "home.html"

**Origen:** brief-personal-stock.md sección 4 + inspección de templates/

**Evidencia:**

- Brief: "Los templates básicos para este inicio son: templates/login.html, templates/home.html"
- Workspace: templates/home.html ya existe (NO existe index.html)

**Resolución:** No hay conflicto real. El brief es correcto, el archivo ya se llama home.html. No se requiere renombrado.

**Documentado en:** Requirements 2, 6, 7 usan directamente "home.html".

### Conflicto 2: Brief asume que cs-chat-rag es base Django

**Origen:** brief-personal-stock.md sección 3 + resumen proyecto previo (bot).md

**Evidencia:**

- Brief dice: "revisar primero cs-chat-rag"
- Realidad: cs-chat-rag es n8n + postgres + nginx + vanilla JS (NO Django)

**Resolución:** Confirmé en inventario que cs-chat-rag NO es base Django reutilizable. Decisión tomada: crear ./app desde cero, solo reutilizar inspiración UI y schema PostgreSQL.

**Documentado en:** Introduction del requirements.md, Decisión 1 de esta devolución.

---

## Qué NO está en este spec

Este spec se limita a base Django + login + home + autenticación básica. NO incluye:

❌ **Permisos por perfil** → Spec `usuarios-demo-perfiles-permisos`
❌ **Roles y fixtures de usuarios** → Spec `usuarios-demo-perfiles-permisos`
❌ **Conexión con n8n/orquestador** → Spec `home-chat-orchestrator-contract`
❌ **Trazabilidad de acciones** → Spec `acciones-trazabilidad-metricas`
❌ **RAG de mails históricos** → Spec `rag-mails-dataset-permissions`
❌ **Trigger Comunicaciones** → Spec `trigger-comunicaciones-email`
❌ **Memoria conversacional** → Spec `memoria-feedback-correcciones`
❌ **Contenido heredado Comustock** → Spec `contenido-heredado-y-navegacion`

En este spec, **cualquier usuario autenticado puede acceder a `/`**. La restricción por perfil se implementa en spec 2.

---

## Próximos pasos

1. ✅ Requirements.md generado y listo para revisión
2. ⏳ Esperando tu aprobación
3. ⏸️ Después: generar design.md (arquitectura técnica, modelos, vistas, configuración detallada)
4. ⏸️ Después: generar tasks.md (lista de tareas con subtareas y criterios de aceptación)

---

## Veredicto y fecha

**Fecha:** 2026-06-21
**Spec:** base-django-login-home
**Fase:** requirements
**Estado:** ✅ Generado exitosamente con formato EARS estricto

**Veredicto:** Requirements completo y listo para aprobación. Todos los acceptance criteria son medibles, testables y sin ambigüedad. Decisiones de inventario aplicadas correctamente. No se detectaron conflictos sin resolver entre brief y estructura real del workspace.
