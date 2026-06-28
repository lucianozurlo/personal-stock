# Validación — usuarios-demo-perfiles-permisos — Tarea 10.1

**Fecha:** 2026-06-23
**Spec:** usuarios-demo-perfiles-permisos
**Tarea:** 10.1 — Actualizar vista de home para incluir perfil y roles en contexto
**Veredicto:** ✅ **COMPLETED**

---

## Qué se implementó

Se modificó `app/core/views.py` (`home_view`) para exponer `perfil` y `roles` del usuario autenticado en el contexto de la vista y en el diccionario `ps_user_data`.

### Cambio en `home_view`

**Antes:**

```python
@login_required
def home_view(request):
    context = {
        'user': request.user,
        'ps_user_data': {
            'firstName': request.user.first_name or request.user.username,
            'username': request.user.username,
            'email': request.user.email,
        }
    }
    return render(request, 'home.html', context)
```

**Después:**

```python
@login_required
def home_view(request):
    user = request.user
    roles_list = list(user.roles.values_list('name', flat=True))
    context = {
        'user': user,
        'perfil': user.perfil,
        'roles': user.roles.all(),
        'ps_user_data': {
            'firstName': user.first_name or user.username,
            'username': user.username,
            'email': user.email,
            'perfil': user.perfil,
            'roles': roles_list,
        }
    }
    return render(request, 'home.html', context)
```

---

## Validación Kiro

### ✅ Criterios de aceptación (tasks.md 10.1)

| Criterio                                                | Estado      | Evidencia                                                                                                                                        |
| ------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Agregar user.perfil al contexto de home_view            | ✅ Cumplido | `'perfil': user.perfil` como clave de primer nivel en context (views.py:34)                                                                      |
| Agregar user.roles.all() al contexto de home_view       | ✅ Cumplido | `'roles': user.roles.all()` como clave de primer nivel en context (views.py:35); `'roles': roles_list` también en ps_user_data (views.py:41)     |
| Verificar que datos se exponen correctamente en session | ✅ Cumplido | `ps_user_data['perfil']` y `ps_user_data['roles']` explícitos; acceso via request.user.perfil / request.user.roles en cualquier view autenticada |
| Tests existentes siguen pasando                         | ✅ Cumplido | 6/6 AuthViewsTest OK — `python -Wa manage.py test core.tests.AuthViewsTest -v 2`                                                                 |

### ✅ Requirements cubiertos

| Requirement                                        | Estado      |
| -------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------- |
| Req 9.1 — perfil en session data                   | ✅ Cumplido | `ps_user_data['perfil']` expuesto en contexto                                                   |
| Req 9.2 — roles en session data                    | ✅ Cumplido | `ps_user_data['roles']` = lista de strings de roles                                             |
| Req 9.3 — perfil y roles accesibles a Django views | ✅ Cumplido | `context['perfil']` y `context['roles']` disponibles como variables de template de primer nivel |

### Output de tests

```
Ran 6 tests in 6.542s
OK
```

- `test_home_view_authenticated` — OK (verifica presencia de 'user' y 'ps_user_data')
- `test_home_view_unauthenticated` — OK
- `test_login_view_get` — OK
- `test_login_view_post_invalid` — OK
- `test_login_view_post_valid` — OK
- `test_logout_view` — OK

---

## Archivos modificados

- `app/core/views.py` — única modificación (líneas 30-43)

---

## Decisión: COMPLETED

La tarea 10.1 cumple completamente con:

- ✅ Todos los criterios de aceptación de tasks.md
- ✅ Requirements 9.1, 9.2, 9.3 de requirements.md
- ✅ Tests existentes siguen pasando
- ✅ Implementación correcta y completa

**Marcada como [x] en tasks.md**

---

## Próximas tareas

- Tarea 10.2: Actualizar template home.html para mostrar perfil y roles
- Tarea 10.3: Write integration test para exposición de perfil/roles
