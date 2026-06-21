# Requirements Document

## Introduction

Este spec cubre la creación de la base Django para Personal Stock y la integración de los templates de login y home ya existentes. El proyecto Django se creará desde cero en `./app/`, configurará conexión a base de datos mediante `dj-database-url`, servirá los templates fuente desde `./templates` (raíz del workspace), implementará autenticación básica con sesión persistente, y reemplazará el usuario hardcodeado "Benja" por el usuario de sesión Django.

**Decisión de inventario confirmada:** `cs-chat-rag` es un proyecto independiente (n8n + postgres + nginx + vanilla JS), NO una base Django reutilizable. Por lo tanto, `./app` se crea desde cero y solo se reutiliza: schema PostgreSQL de memoria conversacional, patrón de orquestación n8n, e inspiración UI de los templates.

**Decisión de naming confirmada:** El archivo fuente se llama `templates/home.html` (NO `index.html`). No hay renombrado necesario.

---

## Glossary

- **Django_App**: El proyecto Django que se creará en `./app/` con `django-admin startproject`.
- **Django_Auth**: Sistema de autenticación integrado de Django (`django.contrib.auth`).
- **Session**: Sesión persistente de Django que almacena el estado de autenticación del usuario entre requests.
- **Template_Source**: Los templates HTML fuente ubicados en `./templates` (raíz del workspace, fuera de `./app`).
- **Static_Assets**: Archivos CSS, JS e imágenes ubicados en `./templates/css/`, `./templates/js/`, `./templates/img/`.
- **DATABASE_URL**: Variable de entorno que especifica la conexión a base de datos en formato URI.
- **dj_database_url**: Librería Python que parsea `DATABASE_URL` y la convierte en configuración de Django.
- **Logged_User**: El usuario autenticado en la sesión Django, accesible como `request.user`.
- **Hardcoded_User**: El valor "Benja" que aparece hardcodeado en `templates/home.html` y `templates/js/app.js`.

---

## Requirements

### Requirement 1: Bootstrap del proyecto Django

**User Story:** Como desarrollador, quiero crear un proyecto Django desde cero en `./app/`, para que sirva como base de la aplicación Personal Stock.

#### Acceptance Criteria

1. WHEN se ejecuta `django-admin startproject config .` dentro de `./app/`, THE Django_App SHALL crear la estructura de proyecto con `manage.py` y carpeta `config/` conteniendo `settings.py`, `urls.py`, `wsgi.py`, `asgi.py`.

2. THE Django_App SHALL incluir `dj-database-url` en `requirements.txt` con versión pinada (formato `dj-database-url==X.Y.Z`).

3. WHEN se importa `dj_database_url` en `settings.py`, THE Django_App SHALL configurar `DATABASES['default']` usando `dj_database_url.parse(os.environ.get('DATABASE_URL'))` para que la variable de entorno `DATABASE_URL` quede cableada en código.

4. THE Django_App SHALL configurar `SECRET_KEY` en `settings.py` usando `os.environ.get('DJANGO_SECRET_KEY')` para que la variable de entorno `DJANGO_SECRET_KEY` quede cableada en código.

5. THE Django_App SHALL incluir en `INSTALLED_APPS` las apps por defecto de Django: `django.contrib.admin`, `django.contrib.auth`, `django.contrib.contenttypes`, `django.contrib.sessions`, `django.contrib.messages`, `django.contrib.staticfiles`.

6. THE Django_App SHALL poder ejecutar `python manage.py migrate` exitosamente, creando `db.sqlite3` en la raíz de `./app/`.

---

### Requirement 2: Configuración de templates fuente

**User Story:** Como desarrollador, quiero configurar Django para servir los templates HTML desde `./templates` (raíz del workspace), para que no haya duplicación de archivos fuente.

#### Acceptance Criteria

1. WHEN se configura `TEMPLATES[0]['DIRS']` en `settings.py`, THE Django_App SHALL incluir la ruta absoluta `BASE_DIR.parent / 'templates'` para que Django busque templates en la carpeta `./templates` fuera de `./app`.

2. THE Django_App SHALL validar que `BASE_DIR` apunta a `/Users/luciano/Desktop/PS-edit/app` y que `BASE_DIR.parent / 'templates'` resuelve a `/Users/luciano/Desktop/PS-edit/templates`.

3. WHEN Django busca un template llamado `home.html`, THE Django_App SHALL encontrar correctamente el archivo `/Users/luciano/Desktop/PS-edit/templates/home.html`.

4. WHEN Django busca un template llamado `login.html`, THE Django_App SHALL encontrar correctamente el archivo `/Users/luciano/Desktop/PS-edit/templates/login.html`.

---

### Requirement 3: Configuración de archivos estáticos

**User Story:** Como desarrollador, quiero configurar Django para servir los assets CSS, JS e imágenes desde `./templates/css/`, `./templates/js/`, `./templates/img/`, para que los templates puedan cargar sus recursos.

#### Acceptance Criteria

1. WHEN se configura `STATICFILES_DIRS` en `settings.py`, THE Django_App SHALL incluir las rutas absolutas:
   - `BASE_DIR.parent / 'templates' / 'css'`
   - `BASE_DIR.parent / 'templates' / 'js'`
   - `BASE_DIR.parent / 'templates' / 'img'`

2. WHEN se ejecuta `python manage.py collectstatic --noinput`, THE Django_App SHALL copiar todos los archivos de `./templates/css/`, `./templates/js/`, `./templates/img/` a `STATIC_ROOT`.

3. WHEN un template referencia `{% static 'css/styles.css' %}`, THE Django_App SHALL resolver correctamente la ruta al archivo `/Users/luciano/Desktop/PS-edit/templates/css/styles.css`.

4. WHEN un template referencia `{% static 'img/personal-stock-logo.svg' %}`, THE Django_App SHALL resolver correctamente la ruta al archivo `/Users/luciano/Desktop/PS-edit/templates/img/personal-stock-logo.svg`.

---

### Requirement 4: Sistema de autenticación básico

**User Story:** Como usuario, quiero poder autenticarme con email y contraseña, para que el sistema reconozca mi identidad y me permita acceder al home.

#### Acceptance Criteria

1. THE Django_App SHALL habilitar `django.contrib.sessions.middleware.SessionMiddleware` y `django.contrib.auth.middleware.AuthenticationMiddleware` en `MIDDLEWARE` para gestionar sesiones y autenticación.

2. WHEN un usuario no autenticado intenta acceder a la ruta `/` (home), THE Django_App SHALL redirigir al usuario a `/login/`.

3. WHEN un usuario ingresa credenciales válidas en `/login/` y envía el formulario, THE Django_App SHALL autenticar al usuario usando `django.contrib.auth.authenticate()` y `login()`.

4. WHEN la autenticación es exitosa, THE Django_App SHALL crear una sesión persistente y redirigir al usuario a `/` (home).

5. WHEN un usuario autenticado accede a `/`, THE Django_App SHALL permitir el acceso sin redirigir a login.

6. WHEN un usuario hace clic en "Cerrar sesión", THE Django_App SHALL ejecutar `django.contrib.auth.logout()` y destruir la sesión, redirigiendo a `/login/`.

---

### Requirement 5: Integración del template login.html

**User Story:** Como usuario, quiero ver el template de login existente en la ruta `/login/`, para que la interfaz visual sea consistente con el diseño entregado.

#### Acceptance Criteria

1. WHEN se crea una vista `login_view` en Django, THE Django_App SHALL renderizar el template `login.html` usando `render(request, 'login.html')`.

2. THE Django_App SHALL configurar la ruta `/login/` en `urls.py` apuntando a `login_view`.

3. WHEN un usuario accede a `/login/`, THE Django_App SHALL responder con el HTML del template `login.html` incluyendo el formulario de login con campos `email` y `password`.

4. WHEN el formulario de login es enviado (POST), THE Django_App SHALL validar credenciales contra `django.contrib.auth` usando el campo `email` como username.

5. WHEN las credenciales son incorrectas, THE Django_App SHALL devolver el template `login.html` con un mensaje de error visible para el usuario.

6. WHEN las credenciales son correctas, THE Django_App SHALL autenticar al usuario, crear sesión persistente y redirigir a `/`.

---

### Requirement 6: Integración del template home.html

**User Story:** Como usuario autenticado, quiero ver el template de home existente en la ruta `/`, para que la interfaz visual sea consistente con el diseño entregado.

#### Acceptance Criteria

1. WHEN se crea una vista `home_view` en Django, THE Django_App SHALL requerir autenticación usando el decorador `@login_required`.

2. THE Django_App SHALL renderizar el template `home.html` usando `render(request, 'home.html', context)` donde `context` incluye el usuario logueado.

3. THE Django_App SHALL configurar la ruta `/` en `urls.py` apuntando a `home_view`.

4. WHEN un usuario autenticado accede a `/`, THE Django_App SHALL responder con el HTML del template `home.html` incluyendo menú lateral, topbar, prompt conversacional y carousel.

5. WHEN un usuario no autenticado accede a `/`, THE Django_App SHALL redirigir a `/login/`.

---

### Requirement 7: Reemplazo de usuario hardcodeado en home.html

**User Story:** Como usuario autenticado, quiero ver mi nombre de pila en el saludo del home, para que la experiencia sea personalizada y no muestre un usuario hardcodeado.

#### Acceptance Criteria

1. WHEN se renderiza `home.html`, THE Django_App SHALL pasar el objeto `user` en el contexto del template.

2. WHEN el template `home.html` contiene `<span id="welcomeTitle">Hola, Benja.</span>`, THE Template_Source SHALL reemplazar "Benja" por `{{ user.first_name }}` para que Django inyecte el nombre del usuario logueado.

3. WHEN un usuario llamado "Luciano" accede a `/`, THE Django_App SHALL renderizar `<span id="welcomeTitle">Hola, Luciano.</span>` en el HTML final.

4. WHEN un usuario sin `first_name` definido accede a `/`, THE Django_App SHALL renderizar `<span id="welcomeTitle">Hola, {{ user.username }}.</span>` como fallback.

---

### Requirement 8: Reemplazo de usuario hardcodeado en app.js

**User Story:** Como usuario autenticado, quiero que los saludos aleatorios en el chat usen mi nombre, para que la experiencia sea personalizada y no muestre un usuario hardcodeado.

#### Acceptance Criteria

1. WHEN el template `home.html` se renderiza, THE Django_App SHALL inyectar una variable JavaScript `window.PS_USER` conteniendo `{ firstName: "{{ user.first_name }}", username: "{{ user.username }}" }` en un bloque `<script>` inline antes de cargar `app.js`.

2. WHEN `app.js` inicializa el array `RANDOM_GREETINGS`, THE Static_Assets SHALL reemplazar todas las ocurrencias de "Benja" por una referencia dinámica a `window.PS_USER.firstName` o `window.PS_USER.username`.

3. WHEN la función `getTimeBasedGreeting()` genera un saludo, THE Static_Assets SHALL reemplazar "Benja" por `window.PS_USER.firstName`.

4. WHEN un usuario llamado "Luciano" accede al home, THE Django_App SHALL garantizar que `RANDOM_GREETINGS` contiene textos como "Hola Luciano!" en lugar de "Hola Benja!".

5. FOR ALL funciones en `app.js` que referencian "Benja", THE Static_Assets SHALL reemplazar el hardcoded string por la variable dinámica `window.PS_USER.firstName`.

---

### Requirement 9: Sesión persistente

**User Story:** Como usuario autenticado, quiero que mi sesión persista entre recargas de página, para que no tenga que volver a autenticarme en cada request.

#### Acceptance Criteria

1. WHEN un usuario se autentica exitosamente, THE Django_App SHALL crear una entrada de sesión en la tabla `django_session` de la base de datos.

2. WHEN un usuario recarga la página `/` después de autenticarse, THE Django_App SHALL reconocer la sesión existente mediante la cookie `sessionid` y mantener al usuario autenticado.

3. WHEN un usuario cierra el navegador y vuelve a abrir `/` dentro del tiempo de expiración de la sesión (por defecto 2 semanas), THE Django_App SHALL mantener al usuario autenticado si el checkbox "Recordarme" estaba marcado.

4. WHEN un usuario no marca el checkbox "Recordarme" y cierra el navegador, THE Django_App SHALL destruir la sesión al cerrar el navegador (sesión no persistente).

5. WHEN la sesión expira o es inválida, THE Django_App SHALL redirigir al usuario a `/login/`.

---

### Requirement 10: Validación de cableo de variables de entorno

**User Story:** Como desarrollador, quiero garantizar que las variables de entorno declaradas en `.env.example` están correctamente cableadas en código, para que no queden declaradas sin uso real.

#### Acceptance Criteria

1. THE Django_App SHALL verificar que `DATABASE_URL` está cableada en `settings.py` mediante `dj_database_url.parse(os.environ.get('DATABASE_URL'))`.

2. THE Django_App SHALL verificar que `DJANGO_SECRET_KEY` está cableada en `settings.py` mediante `os.environ.get('DJANGO_SECRET_KEY')`.

3. WHEN se ejecuta `python manage.py check`, THE Django_App SHALL completar exitosamente sin warnings relacionados con configuración de base de datos o SECRET_KEY.

4. WHEN `DATABASE_URL` no está definida en el entorno, THE Django_App SHALL fallar con un mensaje de error claro indicando que la variable es requerida.

5. WHEN `DJANGO_SECRET_KEY` no está definida en el entorno, THE Django_App SHALL fallar con un mensaje de error claro indicando que la variable es requerida.

---

## Iteration and Feedback Rules

- El modelo DEBE hacer modificaciones si el usuario solicita cambios.
- El modelo DEBE incorporar todo el feedback del usuario antes de proceder.
- El modelo DEBE ofrecer volver a pasos previos si se identifican gaps.

---

## Notes

**Restricciones de permisos:**

- Este spec NO implementa permisos por perfil ni roles. Eso corresponde al spec `usuarios-demo-perfiles-permisos`.
- Cualquier usuario autenticado puede acceder a `/` en este spec.

**Integraciones futuras:**

- La conexión con n8n corresponde al spec `home-chat-orchestrator-contract`.
- La trazabilidad de acciones corresponde al spec `acciones-trazabilidad-metricas`.

**Validación de estructura:**

- Según `structure.md`, la estructura objetivo es:
  ```
  ~/Desktop/PS-edit/
    app/
      manage.py
      config/
      core/
    templates/
      home.html
      login.html
      css/
      js/
      img/
  ```
- Los templates fuente NO se copian a `./app/templates/`. Django los consume directamente desde `./templates` mediante configuración de `TEMPLATES[0]['DIRS']`.

**Decisión de inventario:**

- `cs-chat-rag` es un proyecto independiente (n8n + postgres + nginx + vanilla JS), NO una base Django reutilizable.
- Por lo tanto, `./app` se crea desde cero.
- Solo se reutiliza: schema PostgreSQL de memoria conversacional (en spec futuro), patrón de orquestación n8n (en spec futuro), e inspiración UI de los templates.

**Decisión de naming:**

- El archivo fuente se llama `templates/home.html` (NO `index.html`).
- No hay renombrado necesario.
- Todas las referencias en specs y código apuntan a `home.html`.
