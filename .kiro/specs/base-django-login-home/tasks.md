# Implementation Plan: base-django-login-home

## Overview

Este plan de implementación cubre la creación del proyecto Django desde cero en `./app/`, la configuración de base de datos con `dj-database-url`, la integración de los templates HTML existentes desde `./templates`, la implementación de autenticación básica con sesión persistente, y el reemplazo del usuario hardcodeado "Benja" por datos dinámicos del usuario logueado.

La secuencia sigue los 10 pasos del bootstrap definidos en el design.md, divididos en tareas pequeñas y atómicas con criterios de aceptación verificables.

---

## Tasks

- [x] 1. Crear estructura base del proyecto Django
  - [x] 1.1 Crear carpeta `./app/` y scaffoldear proyecto con django-admin
    - Ejecutar: `mkdir app && cd app && django-admin startproject config .`
    - Verificar que existe `./app/manage.py` y `./app/config/settings.py`
    - Archivos esperados: `manage.py`, `config/__init__.py`, `config/settings.py`, `config/urls.py`, `config/wsgi.py`, `config/asgi.py`
    - _Requirements: 1.1_

  - [x] 1.2 Crear app Django `core`
    - Ejecutar: `python manage.py startapp core` dentro de `./app/`
    - Verificar que existe `./app/core/` con `__init__.py`, `views.py`, `urls.py`, `models.py`, `tests.py`
    - Agregar `'core'` a `INSTALLED_APPS` en `config/settings.py`
    - _Requirements: 1.5_

- [x] 2. Instalar dependencias y configurar entorno
  - [x] 2.1 Crear requirements.txt con versiones confirmadas
    - Crear archivo `./app/requirements.txt` con contenido:
      ```
      Django==5.2.15
      dj-database-url==3.1.2
      asgiref==3.11.1
      sqlparse==0.5.5
      ```
    - Verificar que el archivo existe y contiene las 4 líneas
    - Archivos esperados: `./app/requirements.txt`
    - _Requirements: 1.2_

  - [x] 2.2 Instalar dependencias en el entorno
    - Ejecutar: `pip install -r requirements.txt` desde `./app/`
    - Verificar que `pip list | grep -E "Django|dj-database-url"` muestra las versiones correctas
    - _Requirements: 1.2_

- [x] 3. Configurar settings.py (base de datos, templates, static files)
  - [x] 3.1 Configurar variables de entorno obligatorias
    - Agregar al inicio de `settings.py`:
      ```python
      import os
      import dj_database_url
      ```
    - Reemplazar la línea de `SECRET_KEY` por:
      ```python
      SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
      if not SECRET_KEY:
          raise ValueError('DJANGO_SECRET_KEY no está definida en el entorno')
      ```
    - Verificar que al ejecutar `python manage.py check` sin env vars definidas, Django falla con ValueError claro
    - Archivos esperados: `./app/config/settings.py`
    - _Requirements: 1.4, 10.2, 10.5_

  - [x] 3.2 Configurar DATABASE_URL con dj-database-url
    - Reemplazar el bloque `DATABASES` en `settings.py` por:

      ```python
      DATABASE_URL = os.environ.get('DATABASE_URL')
      if not DATABASE_URL:
          raise ValueError('DATABASE_URL no está definida en el entorno')

      DATABASES = {
          'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
      }
      ```

    - Verificar con `grep "dj_database_url.parse" ./app/config/settings.py` que el cableo está presente
    - Archivos esperados: `./app/config/settings.py`
    - _Requirements: 1.3, 10.1, 10.4_

  - [x] 3.3 Configurar TEMPLATES para consumir desde ./templates
    - Modificar `TEMPLATES[0]['DIRS']` en `settings.py`:
      ```python
      'DIRS': [BASE_DIR.parent / 'templates'],
      ```
    - Verificar que `BASE_DIR.parent / 'templates'` resuelve a `/Users/luciano/Desktop/PS-edit/templates`
    - Archivos esperados: `./app/config/settings.py`
    - _Requirements: 2.1, 2.2_

  - [x] 3.4 Configurar STATICFILES_DIRS para assets en ./templates
    - Agregar después del bloque `STATIC_URL` en `settings.py`:
      ```python
      STATIC_ROOT = BASE_DIR / 'staticfiles'
      STATICFILES_DIRS = [
          BASE_DIR.parent / 'templates' / 'css',
          BASE_DIR.parent / 'templates' / 'js',
          BASE_DIR.parent / 'templates' / 'img',
      ]
      ```
    - Verificar con `grep "STATICFILES_DIRS" ./app/config/settings.py` que las 3 rutas están presentes
    - Archivos esperados: `./app/config/settings.py`
    - _Requirements: 3.1_

  - [x] 3.5 Configurar sesiones persistentes
    - Agregar al final de `settings.py`:
      ```python
      SESSION_ENGINE = 'django.contrib.sessions.backends.db'
      SESSION_COOKIE_AGE = 1209600  # 2 semanas
      SESSION_SAVE_EVERY_REQUEST = False
      SESSION_COOKIE_SECURE = False  # True en producción con HTTPS
      SESSION_COOKIE_HTTPONLY = True
      SESSION_COOKIE_SAMESITE = 'Lax'
      ```
    - Verificar con `grep "SESSION_ENGINE\|SESSION_COOKIE_AGE" ./app/config/settings.py`
    - Archivos esperados: `./app/config/settings.py`
    - _Requirements: 9.1, 9.3, 9.4_

  - [x] 3.6 Configurar ALLOWED_HOSTS y DEBUG
    - Modificar en `settings.py`:
      ```python
      DEBUG = True  # Cambiar a False en producción
      ALLOWED_HOSTS = ['localhost', '127.0.0.1']
      ```
    - Verificar que ambas líneas estén presentes
    - Archivos esperados: `./app/config/settings.py`
    - _Requirements: 1.5_

- [x] 4. Configurar URLs del proyecto
  - [x] 4.1 Crear core/urls.py con rutas de autenticación
    - Crear archivo `./app/core/urls.py` con contenido:

      ```python
      from django.urls import path
      from . import views

      app_name = 'core'

      urlpatterns = [
          path('', views.home_view, name='home'),
          path('login/', views.login_view, name='login'),
          path('logout/', views.logout_view, name='logout'),
      ]
      ```

    - Verificar que el archivo existe y contiene las 3 rutas
    - Archivos esperados: `./app/core/urls.py`
    - _Requirements: 5.2, 6.3_

  - [x] 4.2 Incluir core.urls en config/urls.py
    - Modificar `config/urls.py` para incluir:

      ```python
      from django.contrib import admin
      from django.urls import path, include

      urlpatterns = [
          path('admin/', admin.site.urls),
          path('', include('core.urls')),
      ]
      ```

    - Verificar con `grep "include('core.urls')" ./app/config/urls.py`
    - Archivos esperados: `./app/config/urls.py`
    - _Requirements: 5.2, 6.3_

- [x] 5. Implementar vistas de autenticación
  - [x] 5.1 Implementar login_view en core/views.py
    - Crear función `login_view(request)` en `./app/core/views.py`
    - Comportamiento GET: renderizar `login.html` sin contexto, o redirigir a `/` si ya autenticado
    - Comportamiento POST: recibir `email` y `password`, autenticar con `authenticate(request, username=email, password=password)`
    - Si autenticación exitosa: llamar a `login(request, user)`, configurar expiración de sesión según checkbox "remember_me", redirigir a `/`
    - Si autenticación falla: renderizar `login.html` con `{'error': 'Email o contraseña incorrectos'}`
    - Imports necesarios: `from django.contrib.auth import authenticate, login, logout`, `from django.shortcuts import render, redirect`
    - Verificar que la función existe y tiene los 2 comportamientos (GET y POST)
    - Archivos esperados: `./app/core/views.py`
    - _Requirements: 4.3, 4.4, 5.1, 5.4, 5.5, 5.6, 9.3, 9.4_

  - [x] 5.2 Implementar home_view en core/views.py
    - Crear función `home_view(request)` en `./app/core/views.py` con decorador `@login_required`
    - Renderizar `home.html` con contexto:
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
    - Import necesario: `from django.contrib.auth.decorators import login_required`
    - Configurar `LOGIN_URL = '/login/'` en `settings.py` para que `@login_required` redirija correctamente
    - Verificar que la función existe, tiene el decorador y pasa el contexto correcto
    - Archivos esperados: `./app/core/views.py`, `./app/config/settings.py`
    - _Requirements: 4.2, 4.5, 6.1, 6.2, 6.4, 6.5, 7.1_

  - [x] 5.3 Implementar logout_view en core/views.py
    - Crear función `logout_view(request)` en `./app/core/views.py`
    - Llamar a `logout(request)` para destruir sesión
    - Redirigir a `/login/`
    - Verificar que la función existe y destruye la sesión
    - Archivos esperados: `./app/core/views.py`
    - _Requirements: 4.6_

- [x] 6. Checkpoint - Verificar estructura base funciona
  - Definir `DATABASE_URL=sqlite:///db.sqlite3` y `DJANGO_SECRET_KEY=<generada>` en el entorno
  - Ejecutar `python manage.py check` y verificar que no hay errores
  - Ejecutar `python manage.py migrate` y verificar que `./app/db.sqlite3` se crea
  - Verificar que las 3 vistas existen y las URLs están configuradas
  - _Requirements: 1.6, 10.3_

- [x] 7. Modificar templates HTML para integración Django
  - [x] 7.1 Integrar login.html con Django
    - Agregar `{% load static %}` al inicio de `./templates/login.html`
    - Reemplazar todas las referencias relativas de assets por `{% static 'ruta' %}`
      - `css/login.css` → `{% static 'css/login.css' %}`
      - `img/personal-stock-logo.svg` → `{% static 'img/personal-stock-logo.svg' %}`
      - `img/personal-stock-logo-light.svg` → `{% static 'img/personal-stock-logo-light.svg' %}`
      - `js/login.js` → `{% static 'js/login.js' %}`
    - Agregar `method="post"` y `{% csrf_token %}` dentro del `<form id="loginForm">`
    - Agregar bloque condicional antes del formulario:
      ```django
      {% if error %}
      <div class="login-error" style="color: red; margin-bottom: 1rem;">{{ error }}</div>
      {% endif %}
      ```
    - Verificar que los campos del formulario tienen `name="email"`, `name="password"`, y `name="remember_me"` (checkbox)
    - Archivos esperados: `./templates/login.html`
    - _Requirements: 5.1, 5.3, 5.5_

  - [x] 7.2 Integrar home.html con Django - parte 1 (template tags y assets)
    - Agregar `{% load static %}` al inicio de `./templates/home.html`
    - Reemplazar todas las referencias relativas de assets por `{% static 'ruta' %}`
      - `css/styles.css` → `{% static 'css/styles.css' %}`
      - `img/personal-stock-logo.svg` → `{% static 'img/personal-stock-logo.svg' %}`
      - `img/personal-stock-logo-light.svg` → `{% static 'img/personal-stock-logo-light.svg' %}`
      - `js/app.js` → `{% static 'js/app.js' %}`
    - Verificar con `grep "{% static" ./templates/home.html` que todas las referencias están convertidas
    - Archivos esperados: `./templates/home.html`
    - _Requirements: 6.2, 6.4_

  - [x] 7.3 Integrar home.html con Django - parte 2 (reemplazo de "Benja")
    - Buscar `<span id="welcomeTitle">Hola, Benja.</span>` en `./templates/home.html`
    - Reemplazar por: `<span id="welcomeTitle">Hola, {{ user.first_name|default:user.username }}.</span>`
    - Buscar el dropdown de usuario (clase `.dd-head`) y reemplazar:
      - Avatar: `<span class="avatar">{{ user.first_name.0|upper }}{{ user.last_name.0|upper }}</span>`
      - Nombre: `<div class="nm">{{ user.first_name }} {{ user.last_name }}</div>`
      - Email: `<small>{{ user.email }}</small>`
    - Buscar el botón "Cerrar sesión" (clase `.dd-item.danger`) y agregar: `onclick="window.location.href='{% url 'core:logout' %}'"`
    - Verificar con `grep -i "benja" ./templates/home.html` que no quedan referencias hardcodeadas (debe retornar 0 resultados)
    - Archivos esperados: `./templates/home.html`
    - _Requirements: 7.2, 7.3, 7.4_

  - [x] 7.4 Integrar home.html con Django - parte 3 (inyectar window.PS_USER)
    - Buscar el `<script src="{% static 'js/app.js' %}"></script>` en `./templates/home.html`
    - Agregar ANTES de ese script:
      ```django
      <script>
        window.PS_USER = {
          firstName: "{{ user.first_name|default:user.username }}",
          username: "{{ user.username }}",
          email: "{{ user.email }}"
        };
      </script>
      ```
    - Verificar que `window.PS_USER` se define antes de cargar `app.js`
    - Archivos esperados: `./templates/home.html`
    - _Requirements: 8.1_

- [x] 8. Modificar JavaScript para usar datos dinámicos
  - [x] 8.1 Reemplazar "Benja" en app.js - parte 1 (RANDOM_GREETINGS)
    - Abrir `./templates/js/app.js`
    - Buscar el array `RANDOM_GREETINGS` y reemplazar todas las ocurrencias de `"Benja"` (string literal) por `${window.PS_USER.firstName}` (template literal)
    - Asegurar que todos los strings que contienen "Benja" usan backticks (`) en lugar de comillas simples o dobles
    - Ejemplos de reemplazo:
      - `"Hola Benja!"` → `` `Hola ${window.PS_USER.firstName}!` ``
      - `"¿Todo bien, Benja?"` → `` `¿Todo bien, ${window.PS_USER.firstName}?` ``
    - Verificar con `grep -i "benja" ./templates/js/app.js` que no quedan referencias hardcodeadas (debe retornar 0 resultados si el array es el único lugar)
    - Archivos esperados: `./templates/js/app.js`
    - _Requirements: 8.2, 8.4, 8.5_

  - [x] 8.2 Reemplazar "Benja" en app.js - parte 2 (getTimeBasedGreeting)
    - Buscar la función `getTimeBasedGreeting()` en `./templates/js/app.js`
    - Reemplazar todas las ocurrencias de `"Benja"` en los strings de retorno por `${window.PS_USER.firstName}` o `${name}` si se define una variable local
    - Ejemplo:
      ```javascript
      function getTimeBasedGreeting() {
        const hour = new Date().getHours();
        const name = window.PS_USER.firstName;
        if (hour >= 5 && hour < 12) return `¡Buen día, ${name}!`;
        if (hour >= 12 && hour < 20) return `¡Buenas tardes, ${name}!`;
        return `¡Buenas noches, ${name}!`;
      }
      ```
    - Verificar que la función ya no tiene strings hardcodeados
    - Archivos esperados: `./templates/js/app.js`
    - _Requirements: 8.3, 8.5_

  - [x] 8.3 Agregar validación de PS_USER en app.js
    - Al inicio de `./templates/js/app.js` (después de constantes, antes de funciones), agregar:
      ```javascript
      if (!window.PS_USER || !window.PS_USER.firstName) {
        console.error(
          "PS_USER no está definido. El usuario debe estar autenticado.",
        );
        window.location.href = "/login/";
      }
      ```
    - Verificar que el bloque existe al inicio del archivo
    - Archivos esperados: `./templates/js/app.js`
    - _Requirements: 8.1_

- [x] 9. Checkpoint - Migraciones y creación de superusuario
  - Ejecutar `python manage.py migrate` y verificar que `db.sqlite3` contiene las tablas de Django (auth_user, django_session, etc.)
  - Ejecutar `python manage.py createsuperuser` y crear usuario de prueba con:
    - Username (email): test@personal.com.ar
    - Email: test@personal.com.ar
    - Password: testpass123
    - First name: Luciano
    - Last name: Prueba
  - Verificar que el usuario existe en la base de datos
  - _Requirements: 1.6, 4.3_

- [x] 10. Verificación manual del flujo completo
  - Ejecutar `python manage.py runserver`
  - Acceder a `http://localhost:8000/` sin login → debe redirigir a `/login/`
  - Ingresar credenciales incorrectas → debe mostrar mensaje de error "Email o contraseña incorrectos"
  - Ingresar credenciales correctas (test@personal.com.ar / testpass123) SIN marcar "Recordarme" → debe redirigir a `/` y mostrar home
  - Verificar que el saludo muestra "Hola, Luciano." (no "Hola, Benja.")
  - Verificar que el avatar muestra iniciales "LP"
  - Verificar que el dropdown de usuario muestra "Luciano Prueba" y "test@personal.com.ar"
  - Hacer clic en "Cerrar sesión" → debe redirigir a `/login/` y destruir sesión
  - Login nuevamente CON "Recordarme" marcado → verificar que la sesión persiste al cerrar y reabrir navegador (simular inspeccionando cookie `sessionid` con expiry largo)
  - Verificar que assets CSS, JS, imágenes cargan correctamente (sin errores 404 en consola)
  - Verificar que logo `personal-stock-logo.svg` se muestra correctamente
  - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6, 5.3, 5.5, 5.6, 6.4, 6.5, 7.3, 9.2, 9.3, 9.4_

- [ ] 11. Escribir tests unitarios básicos
  - [x] 11.1 Escribir tests de autenticación en core/tests.py
    - Implementar `test_login_view_get()`: verifica que GET `/login/` retorna 200 y renderiza `login.html`
    - Implementar `test_login_view_post_valid()`: crea usuario, POST con credenciales válidas, verifica redirect a `/` y sesión creada
    - Implementar `test_login_view_post_invalid()`: POST con credenciales inválidas, verifica status 200 y contexto con `error`
    - Implementar `test_home_view_authenticated()`: login y GET `/`, verifica status 200 y contexto con `user` y `ps_user_data`
    - Implementar `test_home_view_unauthenticated()`: GET `/` sin autenticación, verifica redirect a `/login/`
    - Implementar `test_logout_view()`: login, GET `/logout/`, verifica redirect a `/login/` y sesión destruida
    - Ejecutar `python manage.py test core` y verificar que todos pasan
    - Archivos esperados: `./app/core/tests.py`
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6, 5.1, 5.5, 5.6, 6.1, 6.4, 6.5_

  - [x] 11.2 Escribir tests de configuración en core/tests.py
    - Implementar `test_static_files_configuration()`: verifica que `STATICFILES_DIRS` contiene las 3 rutas correctas
    - Implementar `test_template_configuration()`: verifica que `TEMPLATES[0]['DIRS']` contiene `BASE_DIR.parent / 'templates'`
    - Ejecutar `python manage.py test core` y verificar que todos pasan
    - Archivos esperados: `./app/core/tests.py`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1_

- [x] 12. Checkpoint final - Validar contra requirements.md
  - Revisar cada requirement (1-10) en `requirements.md` y verificar que todos los criterios de aceptación están cumplidos
  - Ejecutar `python manage.py check` sin errores
  - Ejecutar `python manage.py test` y verificar que todos los tests pasan (si se implementaron)
  - Confirmar que no quedan referencias a "Benja" hardcodeadas: `grep -ri "benja" ./templates/` debe retornar 0 resultados
  - Confirmar que `DATABASE_URL` y `DJANGO_SECRET_KEY` están cableadas: `grep "dj_database_url.parse\|os.environ.get('DJANGO_SECRET_KEY')" ./app/config/settings.py`
  - Documentar cualquier limitación conocida (SSO no funcional, "Olvidé mi contraseña" no funcional, sin rate limiting)
  - Spec completo y listo para siguiente fase (usuarios-demo-perfiles-permisos)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 10.4, 10.5_

---

## Notes

**Orden de ejecución serializado:**

La implementación debe seguir el orden numérico estricto: **1.1 → 1.2 → 2.1 → 2.2 → 3.1 → 3.2 → 3.3 → ... → 12**

- **Una subtarea por sesión de Claude Code en modo plan**
- **No ejecutar tareas en paralelo** — el Task Dependency Graph queda solo como referencia interna de dependencias lógicas
- Cada subtarea debe completarse y validarse antes de pasar a la siguiente

**Tests unitarios obligatorios:**

- Las tareas 11.1 y 11.2 son **OBLIGATORIAS** para garantizar calidad del spec antes de marcarlo como completed
- No omitir tests para acelerar el MVP

**Checkpoints incluidos:**

- Tarea 6: Verificación de estructura base antes de modificar templates
- Tarea 9: Migraciones y creación de superusuario antes de testing manual
- Tarea 12: Validación final contra requirements.md

**Criterios de aceptación verificables:**

- Cada subtarea especifica archivos esperados y comandos de verificación
- Cada subtarea referencia explícitamente los requirements que cumple

**Archivos a crear:**

- `./app/manage.py` (generado por django-admin)
- `./app/config/settings.py` (generado y modificado)
- `./app/config/urls.py` (generado y modificado)
- `./app/core/views.py` (creado)
- `./app/core/urls.py` (creado)
- `./app/core/tests.py` (modificado)
- `./app/requirements.txt` (creado)
- `./app/db.sqlite3` (generado después de migrate)

**Archivos a modificar:**

- `./templates/login.html` (agregar {% load static %}, {% csrf_token %}, actualizar assets)
- `./templates/home.html` (agregar {% load static %}, reemplazar "Benja", actualizar assets, inyectar PS_USER)
- `./templates/js/app.js` (reemplazar hardcoded "Benja" por window.PS_USER.firstName)

**Archivos a NO modificar:**

- `./templates/css/styles.css` (sin cambios)
- `./templates/css/login.css` (sin cambios)
- `./templates/img/*` (sin cambios)
- `./templates/js/login.js` (sin cambios, a menos que contenga lógica de simulación que debe eliminarse)

**Limitaciones conocidas (fuera de scope):**

- Botón "Iniciar sesión con Microsoft 365" presente en UI pero no funcional (spec futuro: `sso-microsoft365`)
- Link "Olvidé mi contraseña" presente en UI pero no funcional (spec futuro: `password-recovery`)
- Sin permisos por perfil/rol (spec futuro: `usuarios-demo-perfiles-permisos`)
- Sin trazabilidad de login (spec futuro: `acciones-trazabilidad-metricas`)
- Sin rate limiting contra fuerza bruta (spec futuro si requerido)

**Dependencias de specs:**

- Este spec NO depende de otros specs (es el primero del MVP 1)
- Specs que dependen de este: `usuarios-demo-perfiles-permisos`, `home-chat-orchestrator-contract`, `acciones-trazabilidad-metricas`

**Versiones confirmadas:**

```
Django==5.2.15
dj-database-url==3.1.2
asgiref==3.11.1
sqlparse==0.5.5
```

---

## Task Dependency Graph

El siguiente grafo muestra las dependencias lógicas entre tareas. Es **solo referencia interna** para entender relaciones entre tareas.

**IMPORTANTE:** La implementación real debe seguir el orden numérico serializado (1.1 → 1.2 → 2.1 → ... → 12), ejecutando **una subtarea por sesión de Claude Code**. No ejecutar tareas en paralelo.

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "2.1"] },
    { "id": 2, "tasks": ["2.2"] },
    { "id": 3, "tasks": ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6"] },
    { "id": 4, "tasks": ["4.1"] },
    { "id": 5, "tasks": ["4.2"] },
    { "id": 6, "tasks": ["5.1", "5.2", "5.3"] },
    { "id": 7, "tasks": ["7.1", "7.2"] },
    { "id": 8, "tasks": ["7.3"] },
    { "id": 9, "tasks": ["7.4"] },
    { "id": 10, "tasks": ["8.1", "8.2"] },
    { "id": 11, "tasks": ["8.3"] },
    { "id": 12, "tasks": ["11.1", "11.2"] }
  ]
}
```
