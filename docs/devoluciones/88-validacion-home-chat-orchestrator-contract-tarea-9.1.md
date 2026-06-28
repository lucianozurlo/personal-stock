# Devolución: home-chat-orchestrator-contract — Tarea 9.1

**Fecha:** 2026-06-27
**Spec:** home-chat-orchestrator-contract
**Tarea:** 9.1 — Agregar endpoint a core/urls.py
**Veredicto:** ✅ COMPLETED

---

## Qué se validó

La tarea 9.1 requiere agregar `path('api/chat/', views.chat_view, name='chat')` a `app/core/urls.py` y verificar que la ruta responde con 302 cuando el usuario no está autenticado.

## Hallazgos

### Estado de la implementación

La ruta `api/chat/` ya estaba presente en `app/core/urls.py` en el momento de iniciar esta sesión — fue agregada durante la implementación de la tarea 8.1 (implementación de `chat_view`). El estado al comenzar la sesión:

```python
# app/core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/chat/', views.chat_view, name='chat'),  # línea 10
]
```

El config principal (`app/config/urls.py`) incluye las URLs de `core` en la raíz:

```python
path('', include('core.urls')),
```

Por lo tanto, `/api/chat/` es accesible directamente.

### Verificación del comportamiento de autenticación

`chat_view` tiene el decorador `@login_required` (`app/core/views.py:74`), lo que causa un redirect 302 a `/login/` para usuarios no autenticados.

**Test específico ejecutado:**

```
python3 -Wa manage.py test core.tests.ChatViewIntegrationTest.test_unauthenticated_user_gets_redirect -v 2
```

**Resultado:**

```
test_unauthenticated_user_gets_redirect (core.tests.ChatViewIntegrationTest)
Usuario no autenticado recibe redirect (302) a login (Req 8.8 criterio 4) ... ok

Ran 1 test in 0.788s

OK
```

### Suite completa

Test suite completa ejecutada (`python3 -Wa manage.py test core -v 1`):

```
Ran 123 tests in 542.766s
OK
```

Sin errores ni fallos.

---

## Criterios de aceptación — evaluación punto por punto

| Criterio (tasks.md)                                                     | Estado      | Evidencia                                                                        |
| ----------------------------------------------------------------------- | ----------- | -------------------------------------------------------------------------------- |
| Abrir `app/core/urls.py`                                                | ✅ Cumplido | Archivo verificado — contiene la ruta en línea 10                                |
| Importar `chat_view` desde views                                        | ✅ Cumplido | `from . import views` + uso como `views.chat_view` — equivalente funcional       |
| Agregar `path('api/chat/', views.chat_view, name='chat')` a urlpatterns | ✅ Cumplido | `app/core/urls.py:10` — presente al iniciar sesión                               |
| Verificar que la ruta responde 401/302 si no autenticado                | ✅ Cumplido | `test_unauthenticated_user_gets_redirect` → status 302 OK (`tests.py:1525-1528`) |

---

## Veredicto Final: ✅ COMPLETED

La tarea 9.1 cumple TODOS los criterios de aceptación:

1. ✅ La ruta `path('api/chat/', views.chat_view, name='chat')` está presente en `app/core/urls.py:10`
2. ✅ La importación `from . import views` + uso como `views.chat_view` es funcionalmente correcta
3. ✅ La ruta responde con redirect 302 cuando el usuario no está autenticado (verificado por test)
4. ✅ La suite completa de 123 tests pasa sin errores

**Observación técnica:** La ruta fue agregada durante la implementación de la tarea 8.1 (implementación de `chat_view`), no en una sesión separada. Esto es coherente con el flujo de trabajo y no afecta la validación: el criterio está cumplido independientemente del momento de implementación.

**Próximos pasos:**

- Marcar tarea 9.1 como `[x]` en tasks.md
- Actualizar PROGRESO.md con tarea actual: 10.1
- Proceder con Paso 3.4 — implementar tarea 10.1 (checkpoint backend completo) con Claude Code

---

## Notas adicionales

La ruta fue implementada durante la tarea 8.1 (no en una sesión separada para 9.1), lo cual es coherente con el flujo de implementación de `chat_view`. La tarea 9.1 como tal consistió en la verificación del criterio de aceptación.

**Advertencia detectada (no bloqueante):** `datetime.utcnow()` en `app/core/views.py:97` genera `DeprecationWarning` en Python 3.14. No afecta el comportamiento en MVP 1, pero debería corregirse en una sesión posterior. No corresponde a esta tarea.

---

## Archivos involucrados

| Archivo              | Acción                        |
| -------------------- | ----------------------------- |
| `app/core/urls.py`   | Solo lectura — verificado     |
| `app/config/urls.py` | Solo lectura — verificado     |
| `app/core/views.py`  | Solo lectura — verificado     |
| `app/core/tests.py`  | Solo lectura — test ejecutado |
