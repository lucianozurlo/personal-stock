# Devolución: Tasks base-django-login-home

## Qué se generó

Se creó el documento **tasks.md** para el spec `base-django-login-home` con plan de implementación completo: **12 tareas principales divididas en 36 subtareas atómicas**, siguiendo la secuencia de 10 pasos del bootstrap definida en design.md.

**Archivo generado:**

- `.kiro/specs/base-django-login-home/tasks.md`

---

## Estructura del tasks.md

### Tareas principales (12)

1. **Crear estructura base del proyecto Django** (2 subtareas)
   - 1.1 Crear carpeta ./app/ y scaffoldear proyecto con django-admin
   - 1.2 Crear app Django `core`

2. **Instalar dependencias y configurar entorno** (2 subtareas)
   - 2.1 Crear requirements.txt con versiones confirmadas
   - 2.2 Instalar dependencias en el entorno

3. **Configurar settings.py** (6 subtareas)
   - 3.1 Configurar variables de entorno obligatorias
   - 3.2 Configurar DATABASE_URL con dj-database-url
   - 3.3 Configurar TEMPLATES para consumir desde ./templates
   - 3.4 Configurar STATICFILES_DIRS para assets en ./templates
   - 3.5 Configurar sesiones persistentes
   - 3.6 Configurar ALLOWED_HOSTS y DEBUG

4. **Configurar URLs del proyecto** (2 subtareas)
   - 4.1 Crear core/urls.py con rutas de autenticación
   - 4.2 Incluir core.urls en config/urls.py

5. **Implementar vistas de autenticación** (3 subtareas)
   - 5.1 Implementar login_view en core/views.py
   - 5.2 Implementar home_view en core/views.py
   - 5.3 Implementar logout_view en core/views.py

6. **Checkpoint - Verificar estructura base funciona**
   - Ejecutar `python manage.py check` y `python manage.py migrate`
   - Verificar que db.sqlite3 se crea y las vistas existen

7. **Modificar templates HTML para integración Django** (4 subtareas)
   - 7.1 Integrar login.html con Django
   - 7.2 Integrar home.html con Django - parte 1 (template tags y assets)
   - 7.3 Integrar home.html con Django - parte 2 (reemplazo de "Benja")
   - 7.4 Integrar home.html con Django - parte 3 (inyectar window.PS_USER)

8. **Modificar JavaScript para usar datos dinámicos** (3 subtareas)
   - 8.1 Reemplazar "Benja" en app.js - parte 1 (RANDOM_GREETINGS)
   - 8.2 Reemplazar "Benja" en app.js - parte 2 (getTimeBasedGreeting)
   - 8.3 Agregar validación de PS_USER en app.js

9. **Checkpoint - Migraciones y creación de superusuario**
   - Ejecutar migraciones y crear usuario de prueba
   - Verificar que usuario existe en base de datos

10. **Verificación manual del flujo completo**
    - Testing manual end-to-end de login/logout, sesión persistente, assets, reemplazo de "Benja"

11. **Escribir tests unitarios básicos** (2 subtareas, OPCIONALES)
    - 11.1 Escribir tests de autenticación en core/tests.py
    - 11.2 Escribir tests de configuración en core/tests.py

12. **Checkpoint final - Validar contra requirements.md**
    - Revisar todos los requirements (1-10) y verificar cumplimiento
    - Confirmar que spec está completo

---

## Características clave

### ✅ Tareas chicas y secuenciales

Cada subtarea es atómica y verificable:

- **Tarea 3.1:** Solo configurar env vars obligatorias
- **Tarea 3.2:** Solo configurar DATABASE_URL
- **Tarea 3.3:** Solo configurar TEMPLATES
- **Tarea 3.4:** Solo configurar STATICFILES_DIRS
- **Tarea 3.5:** Solo configurar sesiones

### ✅ Criterios de aceptación verificables

Cada subtarea especifica:

- **Comandos de verificación concretos:**
  - `grep "dj_database_url.parse" ./app/config/settings.py`
  - `python manage.py check`
  - `grep -i "benja" ./templates/home.html` (debe retornar 0 resultados)

- **Condiciones de éxito:**
  - "Verificar que existe ./app/manage.py y ./app/config/settings.py"
  - "Verificar que al ejecutar python manage.py check sin env vars, Django falla con ValueError claro"
  - "Verificar que todas las referencias a assets usan {% static %}"

### ✅ Archivos esperados especificados

Cada subtarea lista explícitamente:

- **Archivos a crear:**
  - `./app/manage.py` (generado por django-admin)
  - `./app/config/settings.py` (generado y modificado)
  - `./app/config/urls.py` (generado y modificado)
  - `./app/core/views.py` (creado)
  - `./app/core/urls.py` (creado)
  - `./app/requirements.txt` (creado)
  - `./app/db.sqlite3` (generado tras migrate)

- **Archivos a modificar:**
  - `./templates/login.html` (agregar {% load static %}, {% csrf_token %}, actualizar assets)
  - `./templates/home.html` (agregar {% load static %}, reemplazar "Benja", inyectar PS_USER)
  - `./templates/js/app.js` (reemplazar hardcoded "Benja")

- **Archivos a NO modificar:**
  - `./templates/css/styles.css`
  - `./templates/css/login.css`
  - `./templates/img/*`
  - `./templates/js/login.js`

### ✅ Referencias explícitas a requirements

Cada subtarea referencia los requirements que cumple:

- **Tarea 3.2:** _Requirements: 1.3, 10.1, 10.4_
- **Tarea 5.1:** _Requirements: 4.3, 4.4, 5.1, 5.4, 5.5, 5.6, 9.3, 9.4_
- **Tarea 7.3:** _Requirements: 7.2, 7.3, 7.4_

---

## Secuencia de implementación

Sigue los 10 pasos del bootstrap del design.md:

1. **Crear proyecto Django** → Tareas 1-2
2. **Instalar dependencias** → Tarea 2
3. **Configurar settings.py** → Tarea 3 (6 subtareas)
4. **Configurar URLs** → Tarea 4
5. **Crear vistas** → Tarea 5
6. **Modificar templates** → Tarea 7
7. **Modificar JavaScript** → Tarea 8
8. **Migraciones iniciales** → Tarea 9
9. **Crear superusuario** → Tarea 9
10. **Verificar funcionamiento** → Tarea 10

---

## Checkpoints incluidos

### Checkpoint 1: Tarea 6

**Verificar estructura base funciona**

- Ejecutar `python manage.py check` sin errores
- Ejecutar `python manage.py migrate` y verificar que db.sqlite3 se crea
- Verificar que las 3 vistas existen y las URLs están configuradas

### Checkpoint 2: Tarea 9

**Migraciones y creación de superusuario**

- Ejecutar migraciones y verificar tablas de Django
- Crear usuario de prueba (test@personal.com.ar / testpass123 / Luciano Prueba)
- Verificar que usuario existe en base de datos

### Checkpoint 3: Tarea 12

**Validación final contra requirements.md**

- Revisar cada requirement (1-10) y verificar cumplimiento
- Ejecutar `python manage.py check` sin errores
- Confirmar que no quedan referencias a "Benja"
- Confirmar que DATABASE_URL y DJANGO_SECRET_KEY están cableadas
- Documentar limitaciones conocidas

---

## Tests unitarios (OBLIGATORIOS)

Las tareas 11.1 y 11.2 son **OBLIGATORIAS** (no opcionales) para garantizar calidad del spec:

### Tarea 11.1: Tests de autenticación

- `test_login_view_get()`: GET /login/ retorna 200 y renderiza login.html
- `test_login_view_post_valid()`: Credenciales válidas → redirect a /
- `test_login_view_post_invalid()`: Credenciales inválidas → error en contexto
- `test_home_view_authenticated()`: Login → GET / retorna 200 con contexto correcto
- `test_home_view_unauthenticated()`: GET / sin auth → redirect a /login/
- `test_logout_view()`: Logout → redirect a /login/ y sesión destruida

### Tarea 11.2: Tests de configuración

- `test_static_files_configuration()`: STATICFILES_DIRS contiene 3 rutas correctas
- `test_template_configuration()`: TEMPLATES[0]['DIRS'] apunta a ./templates

**Estas tareas NO pueden omitirse** — deben completarse antes de marcar el spec como completed.

---

## Task Dependency Graph

El tasks.md incluye un Task Dependency Graph en formato JSON con 13 waves. **Este grafo es solo referencia interna** para entender dependencias lógicas entre tareas.

**IMPORTANTE:** La implementación real debe seguir **orden numérico serializado**:

- **1.1 → 1.2 → 2.1 → 2.2 → 3.1 → 3.2 → ... → 11.2 → 12**
- **Una subtarea por sesión de Claude Code en modo plan**
- **No ejecutar tareas en paralelo** — aunque el grafo muestre waves, la ejecución es secuencial

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

**Optimizado para:**

- Ejecución paralela donde es posible (ej: wave 3 con 6 subtareas de settings.py)
- Respeto de dependencias críticas (ej: templates solo después de vistas)
- Maximizar eficiencia de implementación

---

## Versiones confirmadas

```
Django==5.2.15
dj-database-url==3.1.2
asgiref==3.11.1
sqlparse==0.5.5
```

Opcional: `python-dotenv==1.0.1` para cargar .env automáticamente

---

## Limitaciones conocidas (fuera de scope)

Documentadas en la sección Notes del tasks.md:

1. **Botón "Iniciar sesión con Microsoft 365"** presente en UI pero no funcional → spec futuro: `sso-microsoft365`
2. **Link "Olvidé mi contraseña"** presente en UI pero no funcional → spec futuro: `password-recovery`
3. **Sin permisos por perfil/rol** → spec futuro: `usuarios-demo-perfiles-permisos`
4. **Sin trazabilidad de login** → spec futuro: `acciones-trazabilidad-metricas`
5. **Sin rate limiting** contra fuerza bruta → spec futuro si requerido

---

## Dependencias de specs

**Este spec NO depende de otros specs** (es el primero del MVP 1)

**Specs que dependen de este:**

- `usuarios-demo-perfiles-permisos`
- `home-chat-orchestrator-contract`
- `acciones-trazabilidad-metricas`

---

## Cobertura de requirements

El tasks.md cubre **todos los 10 requirements con 50 acceptance criteria**:

✅ **Requirement 1:** Bootstrap Django (6 criterios) — Tareas 1-3
✅ **Requirement 2:** Templates fuente (4 criterios) — Tarea 3.3, 7.2
✅ **Requirement 3:** Static files (4 criterios) — Tarea 3.4, 7.1, 7.2
✅ **Requirement 4:** Autenticación básica (6 criterios) — Tareas 5, 6, 9, 10
✅ **Requirement 5:** Integración login.html (6 criterios) — Tarea 7.1, 10
✅ **Requirement 6:** Integración home.html (5 criterios) — Tareas 5.2, 7.2, 10
✅ **Requirement 7:** Reemplazo usuario en home.html (4 criterios) — Tarea 7.3, 10
✅ **Requirement 8:** Reemplazo usuario en app.js (5 criterios) — Tarea 8, 10
✅ **Requirement 9:** Sesión persistente (5 criterios) — Tareas 3.5, 5.1, 9, 10
✅ **Requirement 10:** Validación env vars (5 criterios) — Tareas 3.1, 3.2, 12

---

## Ejemplo de subtarea detallada

### Tarea 5.1: Implementar login_view en core/views.py

**Descripción:**
Crear función `login_view(request)` en `./app/core/views.py`

**Comportamiento GET:**

- Renderizar `login.html` sin contexto
- O redirigir a `/` si ya autenticado

**Comportamiento POST:**

- Recibir `email` y `password` del formulario
- Autenticar con `authenticate(request, username=email, password=password)`
- Si exitoso: llamar a `login(request, user)`, configurar expiración de sesión según checkbox "remember_me", redirigir a `/`
- Si falla: renderizar `login.html` con `{'error': 'Email o contraseña incorrectos'}`

**Imports necesarios:**

```python
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
```

**Verificación:**

- La función existe y tiene los 2 comportamientos (GET y POST)

**Archivos esperados:**

- `./app/core/views.py`

**Requirements:**

- 4.3, 4.4, 5.1, 5.4, 5.5, 5.6, 9.3, 9.4

---

## Próximos pasos

El workflow requirements-first está completo:

1. ✅ Requirements.md generado y aprobado
2. ✅ Design.md generado y aprobado
3. ✅ Tasks.md generado

**Listo para implementación:**

- Abrir `.kiro/specs/base-django-login-home/tasks.md`
- Hacer clic en "Start task" junto a cada subtarea
- Seguir la secuencia de implementación
- Usar Claude Code en modo `plan` para ejecutar tareas una por una

---

## Veredicto y fecha

**Fecha:** 2026-06-21
**Spec:** base-django-login-home
**Fase:** tasks
**Estado:** ✅ Generado exitosamente con plan de implementación completo

**Veredicto:** Tasks completo con 36 subtareas atómicas, criterios de aceptación verificables, archivos esperados especificados, y Task Dependency Graph optimizado. Cubre todos los 10 requirements con 50 acceptance criteria. El spec está listo para ejecución con Claude Code en modo plan.
