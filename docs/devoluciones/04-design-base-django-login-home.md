# Devolución: Design base-django-login-home

## Qué se generó

Se creó el documento **design.md** para el spec `base-django-login-home` con diseño técnico detallado que cubre la arquitectura Django, configuración, vistas, templates, models, error handling, testing strategy y secuencia de implementación.

**Archivo generado:**

- `.kiro/specs/base-django-login-home/design.md`

---

## Alcance del diseño

El documento de design.md define la arquitectura técnica para implementar los 10 requirements aprobados:

### 1. Overview — Arquitectura General

**Diagrama de arquitectura:**

```
Browser → Django Application
         ├── Auth Middleware
         ├── Views Layer (login_view, home_view, logout_view)
         ├── Templates (./templates/home.html, login.html)
         ├── Static Assets (./templates/css|js|img)
         └── SQLite Database
```

**Flujo de autenticación:**

- Usuario accede a `/` → redirect a `/login/` si no autenticado
- Ingresa credenciales → Django valida contra DB
- Si válidas → crea sesión en `django_session` → redirect a `/`
- Si inválidas → renderiza login.html con mensaje de error
- Usuario autenticado accede a `/` → renderiza home.html con contexto de usuario

**Estructura de carpetas:**

```
PS-edit/
  app/                       ← NUEVO: Django project
    manage.py
    config/                  ← django-admin startproject config .
      settings.py            ← MODIFICADO: DB, templates, static
      urls.py                ← MODIFICADO: include core.urls
    core/                    ← NUEVA app Django
      views.py               ← login_view, home_view, logout_view
      urls.py                ← URL patterns
      tests.py               ← Unit tests
    db.sqlite3              ← Generado tras migrate
    requirements.txt
  templates/                 ← EXISTENTE: templates fuente
    home.html               ← MODIFICADO: Django tags, reemplazo "Benja"
    login.html              ← MODIFICADO: Django tags, CSRF
    css/, js/, img/
```

### 2. Architecture — Configuración Django

**Django Project Structure:**

- Proyecto creado con `django-admin startproject config .` dentro de `./app/`
- Naming: `config/` para configuración, `core/` para lógica base
- Justificación: Facilita agregar más apps Django en specs futuros

**settings.py — Configuración de templates:**

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.parent / 'templates'],  # ← ./templates fuera de ./app
        'APP_DIRS': True,
        ...
    },
]
```

**settings.py — Configuración de static files:**

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR.parent / 'templates' / 'css',
    BASE_DIR.parent / 'templates' / 'js',
    BASE_DIR.parent / 'templates' / 'img',
]
```

**settings.py — Configuración de base de datos:**

```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}
```

**settings.py — Configuración de sesiones:**

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 semanas
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_SECURE = False  # True en producción HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

**URL Routing:**

- `config/urls.py`: Incluye `core.urls`
- `core/urls.py`: Define rutas `/`, `/login/`, `/logout/`

**Middleware Stack (orden crítico):**

1. SecurityMiddleware
2. SessionMiddleware ← gestiona sesiones
3. CommonMiddleware
4. CsrfViewMiddleware
5. AuthenticationMiddleware ← gestiona autenticación
6. MessageMiddleware
7. ClickjackingMiddleware

### 3. Components and Interfaces — Vistas y Templates

**login_view:**

- **GET**: Renderiza `login.html`, redirige a `/` si ya autenticado
- **POST**:
  - Recibe `email` y `password`
  - Usa `email` como `username` (Django auth espera username)
  - Llama `authenticate(request, username=email, password=password)`
  - Si exitoso: `login(request, user)`, configura session expiry según checkbox "Recordarme", redirige a `/`
  - Si falla: renderiza `login.html` con error "Email o contraseña incorrectos"

**home_view:**

- Requiere autenticación vía `@login_required`
- Redirige automáticamente a `/login/` si no autenticado
- Renderiza `home.html` con contexto:
  ```python
  context = {
      'user': request.user,
      'ps_user_data': {
          'firstName': request.user.first_name or request.user.username,
          'username': request.user.username,
          'email': request.user.email,
      }
  }
  ```
- Serializa `ps_user_data` a JSON e inyecta como `window.PS_USER`

**logout_view:**

- Llama `logout(request)` para destruir sesión
- Redirige a `/login/`
- Idempotente (no requiere autenticación previa)

**Modificaciones en login.html:**

1. Agregar `{% load static %}`
2. Actualizar assets: `<link rel="stylesheet" href="{% static 'css/login.css' %}">`
3. Agregar `{% csrf_token %}` en formulario
4. Mostrar mensajes de error: `{% if error %}<div class="login-error">{{ error }}</div>{% endif %}`

**Modificaciones en home.html:**

1. Agregar `{% load static %}`
2. Actualizar assets: `{% static 'css/styles.css' %}`, `{% static 'img/personal-stock-logo.svg' %}`
3. Reemplazar saludo: `<span id="welcomeTitle">Hola, {{ user.first_name|default:user.username }}.</span>`
4. Inyectar datos de usuario para JS:
   ```django
   <script>
     window.PS_USER = {
       firstName: "{{ user.first_name|default:user.username }}",
       username: "{{ user.username }}",
       email: "{{ user.email }}"
     };
   </script>
   <script src="{% static 'js/app.js' %}"></script>
   ```
5. Actualizar menú de usuario con datos dinámicos
6. Hacer funcional botón "Cerrar sesión": `onclick="window.location.href='{% url 'core:logout' %}'"`

**Modificaciones en app.js:**

1. Reemplazar `RANDOM_GREETINGS` con interpolación dinámica:
   ```javascript
   const RANDOM_GREETINGS = [
     `Hola ${window.PS_USER.firstName}!`,
     "__TIME_BASED__",
     `¿Todo bien, ${window.PS_USER.firstName}?`,
     // ... más saludos con interpolación
   ];
   ```
2. Reemplazar `getTimeBasedGreeting()`:
   ```javascript
   function getTimeBasedGreeting() {
     const hour = new Date().getHours();
     const name = window.PS_USER.firstName;
     if (hour >= 5 && hour < 12) return `¡Buen día, ${name}!`;
     if (hour >= 12 && hour < 20) return `¡Buenas tardes, ${name}!`;
     return `¡Buenas noches, ${name}!`;
   }
   ```
3. Agregar validación de PS_USER:
   ```javascript
   if (!window.PS_USER || !window.PS_USER.firstName) {
     console.error(
       "PS_USER no está definido. El usuario debe estar autenticado.",
     );
     window.location.href = "/login/";
   }
   ```

**Modificaciones en login.js:**

- Deshabilitar simulación de login (si existe)
- Formulario debe hacer POST real a `/login/`
- Mantener funcionalidad UI (toggle password visibility, toggle tema)

### 4. Data Models

**Django User Model (estándar):**

- Se usa `django.contrib.auth.models.User` por defecto
- Justificación: Cumple requirements de este spec, se extenderá en spec futuro
- Campos relevantes: `username`, `email`, `password`, `first_name`, `last_name`, `is_active`, `is_staff`, `is_superuser`, `date_joined`, `last_login`
- Decisión de naming: `username` se usa para almacenar el email

**Session Model (automático):**

- Django gestiona sesiones con `django.contrib.sessions.models.Session`
- Esquema tabla `django_session`:
  - `session_key`: VARCHAR(40) PRIMARY KEY (cookie sessionid)
  - `session_data`: TEXT (datos serializados: \_auth_user_id, \_auth_user_backend, \_auth_user_hash)
  - `expire_date`: DATETIME
- Flujo: Usuario ingresa credenciales → Django valida → crea entrada en django_session → envía cookie sessionid → en cada request, SessionMiddleware lee cookie y carga session_data → AuthenticationMiddleware usa \_auth_user_id para cargar request.user

### 5. Error Handling

**Authentication Errors:**

1. Credenciales incorrectas: `authenticate()` retorna None → renderiza login.html con error (HTTP 200, no 401)
2. Usuario inactivo (is_active=False): Mismo manejo que credenciales incorrectas (no revelar existencia)
3. CSRF token inválido: Middleware retorna 403 Forbidden
4. Sesión expirada: `@login_required` redirige a `/login/` (sin mensaje de error, comportamiento esperado)
5. Base de datos no disponible: `OperationalError` → Django retorna 500

**Static Files Errors:**

1. Asset no encontrado: Dev server retorna 404, browser muestra error en consola, template sigue renderizando
2. STATICFILES_DIRS mal configurada: `collectstatic` falla con FileNotFoundError (detectado en desarrollo)

**Template Rendering Errors:**

1. Template no encontrado: `TemplateDoesNotExist` exception → 500 si DEBUG=False
2. Variable no definida: Django templates son tolerantes, renderiza string vacío, usar `|default:` filter

### 6. Testing Strategy

**Unit Tests obligatorios (./app/core/tests.py):**

1. `test_login_view_get`: GET /login/ retorna 200, renderiza login.html, usuario autenticado redirige a /
2. `test_login_view_post_valid`: Credenciales válidas → redirect a /, request.user.is_authenticated es True
3. `test_login_view_post_invalid`: Credenciales inválidas → 200, contexto contiene error, is_authenticated es False
4. `test_login_remember_me`: Checkbox marcado → session expiry 2 semanas, sin marcar → expiry 0
5. `test_home_view_authenticated`: Login → GET / retorna 200, renderiza home.html, contexto contiene user y ps_user_data
6. `test_home_view_unauthenticated`: GET / sin auth → redirect a /login/
7. `test_logout_view`: Login → GET /logout/ → redirect a /login/, sesión destruida
8. `test_static_files_configuration`: STATICFILES_DIRS contiene rutas correctas, archivos accesibles
9. `test_template_configuration`: TEMPLATES[0]['DIRS'] correcto, login.html y home.html encontrados

**Integration Tests (opcionales, recomendados):**

1. `test_full_login_flow`: Usuario accede a / → redirect login → ingresa credenciales → redirect / → ve nombre personalizado → logout → redirect login
2. `test_session_persistence`: Login con "Recordarme" → cerrar navegador → reabrir → usuario sigue autenticado

**Manual Testing Checklist:**

- [ ] Crear usuario de prueba: `python manage.py createsuperuser`
- [ ] Acceder a `/` sin login → redirige a `/login/`
- [ ] Login con credenciales incorrectas → muestra error
- [ ] Login con credenciales correctas → redirige a `/`
- [ ] Home muestra nombre del usuario (no "Benja")
- [ ] Saludo aleatorio usa nombre del usuario
- [ ] Avatar muestra iniciales del usuario
- [ ] Dropdown muestra email correcto
- [ ] Cerrar sesión → redirige a `/login/` y destruye sesión
- [ ] Login con "Recordarme" → sesión persiste
- [ ] Login sin "Recordarme" → sesión expira al cerrar navegador
- [ ] Assets cargan correctamente
- [ ] Logo de Personal Stock se muestra

### 7. Implementation Notes

**Bootstrap Sequence (orden recomendado):**

1. Crear proyecto Django: `cd ~/Desktop/PS-edit; mkdir app; cd app; django-admin startproject config .; python manage.py startapp core`
2. Instalar dependencias: `pip install dj-database-url; pip freeze > requirements.txt`
3. Configurar settings.py: agregar core a INSTALLED_APPS, configurar TEMPLATES, STATICFILES_DIRS, DATABASES, SECRET_KEY
4. Configurar URLs: crear core/urls.py, incluir en config/urls.py
5. Crear vistas: implementar login_view, home_view, logout_view en core/views.py
6. Modificar templates: agregar template tags, actualizar assets, reemplazar "Benja", inyectar PS_USER
7. Modificar JavaScript: reemplazar hardcoded "Benja" por window.PS_USER.firstName
8. Migraciones iniciales: `python manage.py migrate`
9. Crear superusuario: `python manage.py createsuperuser`
10. Verificar: `python manage.py runserver`

**Environment Variables Setup:**

```bash
cp .env.example .env
# Editar .env con valores reales:
# DJANGO_SECRET_KEY=tu-secret-key-generada
# DATABASE_URL=sqlite:///db.sqlite3
# N8N_WEBHOOK_URL=http://localhost:5678/webhook-test/personal-stock-orchestrator
```

**Cargar variables en settings.py:**

```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('DJANGO_SECRET_KEY no está definida en el entorno')

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError('DATABASE_URL no está definida en el entorno')

DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}
```

**Security Considerations (MVP 1 desarrollo local):**

1. SECRET_KEY única, generada con `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`, NUNCA commitear
2. DEBUG = True en desarrollo, False en producción
3. ALLOWED_HOSTS = ['localhost', '127.0.0.1'] en desarrollo
4. CSRF habilitada por defecto, todos los forms POST con {% csrf_token %}
5. SESSION_COOKIE_SECURE = False en desarrollo (HTTP), True en producción (HTTPS)
6. SESSION_COOKIE_HTTPONLY = True siempre (previene XSS)
7. Django hashea passwords automáticamente con PBKDF2

**Performance Considerations (100 usuarios demo):**

1. SQLite suficiente para desarrollo local, migrar a PostgreSQL en spec futuro
2. Database-backed sessions suficientes, SESSION_SAVE_EVERY_REQUEST = False reduce writes
3. conn_max_age=600 en DATABASES reutiliza conexiones
4. Django cachea templates compilados automáticamente en producción

**Limitations and Future Work:**

1. Autenticación solo por email/password (no SSO Microsoft 365) → spec futuro
2. Sin recuperación de password → spec futuro password-recovery
3. Sin perfiles ni roles → spec usuarios-demo-perfiles-permisos
4. Sin validación de email corporativo → agregar validación @personal.com.ar si requerido
5. Sin trazabilidad de login → spec acciones-trazabilidad-metricas
6. Sin rate limiting → agregar django-ratelimit si requerido

**Dependencies:**

```
Django==5.2.15
dj-database-url==3.1.2
asgiref==3.11.1
sqlparse==0.5.5
```

Opcional: `python-dotenv==1.0.1` para cargar .env automáticamente

**File Modifications Summary:**

- **Crear:** manage.py, config/settings.py, config/urls.py, config/wsgi.py, config/asgi.py, core/views.py, core/urls.py, core/tests.py, requirements.txt
- **Modificar:** templates/login.html, templates/home.html, templates/js/app.js
- **NO modificar:** templates/js/login.js, templates/css/, templates/img/

### 8. Diagrams

**Component Interaction Diagram:**

```
Browser → Django Application
         ├── Session Middleware
         ├── Auth Middleware
         ├── login_view → Templates → Static Files
         ├── home_view → Templates (inject PS_USER) → Static Files
         └── logout_view

         login_view → authenticate → Database
         Session Middleware → read/write session → Database
         home_view → @login_required → Auth Middleware
```

**Session Flow Diagram:**

```
[Unauthenticated]
  ↓ GET /
[LoginPage]
  ↓ Enter credentials
  ├─ POST /login/ (valid) → [Authenticated]
  └─ POST /login/ (invalid) → [LoginPage]

[Authenticated]
  ↓ GET /
[HomePage]
  ↓ Interact with UI
  ├─ Session renewed → [Authenticated]
  ├─ Session expires → [Unauthenticated]
  └─ GET /logout/ → [Unauthenticated]
```

### 9. Acceptance Criteria Validation

El documento incluye validación detallada de cada criterio de los 10 requirements:

- **Requirement 1:** Bootstrap Django (6 criterios validados)
- **Requirement 2:** Templates fuente (4 criterios validados)
- **Requirement 3:** Static files (4 criterios validados)
- **Requirement 4:** Autenticación básica (6 criterios validados)
- **Requirement 5:** Integración login.html (6 criterios validados)
- **Requirement 6:** Integración home.html (5 criterios validados)
- **Requirement 7:** Reemplazo usuario en home.html (4 criterios validados)
- **Requirement 8:** Reemplazo usuario en app.js (5 criterios validados)
- **Requirement 9:** Sesión persistente (5 criterios validados)
- **Requirement 10:** Validación cableo env vars (5 criterios validados)

---

## Decisiones técnicas aplicadas

### Decisión 1: Django naming convention

**Decisión:** Proyecto Django con `django-admin startproject config .` dentro de `./app/`, app principal `core/`

**Justificación:**

- `config/` hace explícito que contiene configuración, no lógica de negocio
- `core/` contendrá lógica base (autenticación, vistas, modelos)
- Facilita agregar más apps Django en specs futuros (ej: `communication`, `metrics`)

### Decisión 2: User model estándar

**Decisión:** Usar `django.contrib.auth.models.User` por defecto, NO crear custom User model en este spec

**Justificación:**

- Cumple con requirements de este spec (autenticación básica)
- En spec `usuarios-demo-perfiles-permisos` se extenderá con AbstractUser
- No tiene sentido crear custom User model si se va a reemplazar en el siguiente spec

### Decisión 3: Email como username

**Decisión:** Campo `username` de User model se usa para almacenar el email

**Justificación:**

- Django auth requiere campo `username` único
- Más simple usar email como username que crear backend de autenticación custom en este spec base

### Decisión 4: Session expiry con checkbox "Recordarme"

**Decisión:**

- Checkbox marcado: `request.session.set_expiry(1209600)` (2 semanas)
- Checkbox NO marcado: `request.session.set_expiry(0)` (sesión de navegador)

**Justificación:**

- Comportamiento estándar de aplicaciones web
- Seguridad balanceada con UX (usuario decide cuánto tiempo persistir sesión)

### Decisión 5: Middleware order

**Decisión:** SessionMiddleware antes de AuthenticationMiddleware

**Justificación:**

- SessionMiddleware debe cargar datos de sesión primero
- AuthenticationMiddleware necesita acceder a la sesión para cargar request.user
- Orden crítico para funcionamiento correcto

### Decisión 6: Inyección de window.PS_USER

**Decisión:** Serializar `ps_user_data` a JSON e inyectar como `<script>window.PS_USER = {...}</script>` antes de cargar app.js

**Justificación:**

- Permite a JavaScript acceder a datos del usuario de forma segura
- No requiere llamadas AJAX adicionales
- Datos renderizados server-side, no expuestos en endpoint público

### Decisión 7: Error messages en login

**Decisión:** Mensaje genérico "Email o contraseña incorrectos" para credenciales inválidas o usuario inactivo

**Justificación:**

- No revelar si el usuario existe (seguridad)
- Previene enumeración de usuarios

### Decisión 8: Dependencies pinning

**Decisión:** Django==5.2.15, dj-database-url==3.1.2, asgiref==3.11.1, sqlparse==0.5.5

**Justificación:**

- Django 5.2.15: LTS release, soporte extendido, estable y con mejoras de performance
- dj-database-url 3.1.2: Última versión estable, compatible con Django 5.2
- asgiref 3.11.1: ASGI server dependency de Django
- sqlparse 0.5.5: SQL parsing library dependency de Django

---

## Diagramas incluidos

1. **Arquitectura general** (Browser → Django → Database)
2. **Flujo de autenticación** (secuencia de login/logout)
3. **Component Interaction Diagram** (interacción entre componentes)
4. **Session Flow Diagram** (estados de sesión)
5. **Directory Structure Diagram** (estructura de carpetas con anotaciones)

---

## Validación contra requirements

El documento valida que el diseño cubre todos los acceptance criteria de los 10 requirements:

✅ **Requirement 1:** Bootstrap Django (config/, core/, settings.py configurado)
✅ **Requirement 2:** Templates fuente (TEMPLATES[0]['DIRS'] apunta a ./templates)
✅ **Requirement 3:** Static files (STATICFILES_DIRS configurado)
✅ **Requirement 4:** Autenticación básica (SessionMiddleware, AuthenticationMiddleware, redirect a login)
✅ **Requirement 5:** Integración login.html (login_view, ruta /login/, validación credenciales)
✅ **Requirement 6:** Integración home.html (home_view con @login_required, ruta /)
✅ **Requirement 7:** Reemplazo usuario en home.html ({{ user.first_name }}, inyección de contexto)
✅ **Requirement 8:** Reemplazo usuario en app.js (window.PS_USER, interpolación dinámica)
✅ **Requirement 9:** Sesión persistente (django_session table, sessionid cookie, checkbox "Recordarme")
✅ **Requirement 10:** Validación env vars (DATABASE_URL y DJANGO_SECRET_KEY cableadas, raise ValueError si faltan)

---

## Próximos pasos

1. ✅ Requirements.md aprobado
2. ✅ Design.md generado
3. ⏳ Siguiente: generar tasks.md (lista de tareas con subtareas y criterios de aceptación)
4. ⏸️ Después: implementar tareas una por una con Claude Code en modo plan

---

## Veredicto y fecha

**Fecha:** 2026-06-21
**Spec:** base-django-login-home
**Fase:** design
**Estado:** ✅ Generado exitosamente con arquitectura técnica detallada

**Veredicto:** Design completo y listo para aprobación. Todos los requirements tienen diseño técnico detallado, vistas definidas con comportamiento exacto, templates con modificaciones específicas, testing strategy completa, y secuencia de implementación clara. El diseño respeta todas las restricciones de tech.md, structure.md y security-permissions.md. No hay ambigüedades ni decisiones pendientes.
