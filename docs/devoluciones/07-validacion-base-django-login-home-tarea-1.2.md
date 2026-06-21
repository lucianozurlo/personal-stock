# Validación: base-django-login-home — Tarea 1.2

**Fecha:** 21 de junio de 2026
**Spec:** base-django-login-home
**Tarea:** 1.2 — Crear app Django `core`
**Validador:** Kiro (orchestrator)
**Contexto:** Claude Code reportó criterios cumplidos, requiere validación contra requirements.md y tasks.md

---

## Criterios de Aceptación (tasks.md)

| Criterio                        | Estado | Evidencia                                                                        |
| ------------------------------- | ------ | -------------------------------------------------------------------------------- |
| Existe `./app/core/__init__.py` | ✅     | `ls app/core/` → `__init__.py` presente                                          |
| Existe `./app/core/views.py`    | ✅     | `ls app/core/` → `views.py` presente                                             |
| Existe `./app/core/urls.py`     | ✅     | `ls app/core/` → `urls.py` presente con `app_name = 'core'` y `urlpatterns = []` |
| Existe `./app/core/models.py`   | ✅     | `ls app/core/` → `models.py` presente                                            |
| Existe `./app/core/tests.py`    | ✅     | `ls app/core/` → `tests.py` presente                                             |
| `'core'` en INSTALLED_APPS      | ✅     | `grep "'core'" app/config/settings.py` → `'core',` en línea 40                   |
| `python manage.py check`        | ✅     | Ejecutado exitosamente: "System check identified no issues (0 silenced)"         |

---

## Validación contra Requirements.md

### Requirement 1.5

> THE Django_App SHALL incluir en `INSTALLED_APPS` las apps por defecto de Django: `django.contrib.admin`, `django.contrib.auth`, `django.contrib.contenttypes`, `django.contrib.sessions`, `django.contrib.messages`, `django.contrib.staticfiles`.

**Validación:**

- La tarea 1.2 crea la app `core` y la agrega a `INSTALLED_APPS`
- Las apps por defecto ya estaban presentes desde la tarea 1.1 (scaffolding inicial)
- Este criterio de aceptación está cumplido

**Evidencia adicional:**

```bash
grep "django.contrib" app/config/settings.py
```

---

## Hallazgos

### ✅ Cumplimiento total

1. **Estructura de archivos**: La app `core` fue creada correctamente con todos los archivos base de Django (`__init__.py`, `admin.py`, `apps.py`, `models.py`, `views.py`, `tests.py`, `migrations/`)

2. **Archivo urls.py**: Creado manualmente con la estructura correcta:
   - `app_name = 'core'` declarado correctamente
   - `urlpatterns = []` inicializado (se poblará en tarea 4.1)

3. **Integración con settings.py**: La app `'core'` fue agregada correctamente a `INSTALLED_APPS` en `config/settings.py`

4. **System check**: El comando `python3 manage.py check` ejecuta sin errores ni warnings, confirmando que:
   - La app está correctamente registrada
   - No hay errores de configuración
   - La estructura Django es válida

### ⚠️ Observaciones menores (no bloquean completed)

- La tarea especifica "Ejecutar: `python manage.py startapp core`", pero en este sistema el comando es `python3` (no `python`). Esto es una diferencia de entorno, no un problema de implementación.

---

## Veredicto

**COMPLETED** ✅

La tarea 1.2 cumple **todos los criterios de aceptación** definidos en tasks.md:

1. ✅ Todos los archivos esperados existen
2. ✅ `urls.py` tiene la estructura correcta con `app_name = 'core'` y `urlpatterns = []`
3. ✅ `'core'` está presente en `INSTALLED_APPS`
4. ✅ `python manage.py check` (o `python3 manage.py check`) ejecuta sin issues

La tarea también cumple con el Requirement 1.5 de requirements.md (apps por defecto en INSTALLED_APPS, heredadas de tarea 1.1).

**La tarea 1.2 ya está marcada como [x] completed en tasks.md. Validación confirmada.**

---

## Siguiente paso

Proceder con **tarea 2.1**: Crear `requirements.txt` con versiones confirmadas:

- Django==5.2.15
- dj-database-url==3.1.2
- asgiref==3.11.1
- sqlparse==0.5.5
