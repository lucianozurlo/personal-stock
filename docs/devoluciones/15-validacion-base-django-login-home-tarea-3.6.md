# Validación Tarea 3.6: Configurar ALLOWED_HOSTS y DEBUG

## Metadata

**Fecha:** 21 de junio de 2026
**Spec:** base-django-login-home
**Tarea:** 3.6 - Configurar ALLOWED_HOSTS y DEBUG
**Revisor:** Kiro (orquestador de spec)
**Implementador:** Claude Code (modo plan)

---

## Reporte de Claude Code

Claude Code reportó:

| Criterio                                            | Estado | Evidencia                                                       |
| --------------------------------------------------- | ------ | --------------------------------------------------------------- |
| DEBUG = True presente en settings.py                | ✅     | settings.py:31 — ya existía, sin cambios                        |
| ALLOWED_HOSTS = ['localhost', '127.0.0.1'] presente | ✅     | settings.py:33 — actualizado de [] a ['localhost', '127.0.0.1'] |
| Único archivo modificado: ./app/config/settings.py  | ✅     | Confirmado                                                      |

---

## Hallazgos de Validación

### ✅ Criterio de Aceptación Principal

**La tarea 3.6 requiere:**

```python
DEBUG = True  # Cambiar a False en producción
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

**Estado del código en settings.py:**

- **Línea 31:** `DEBUG = True` → **PRESENTE** ✅
- **Línea 33:** `ALLOWED_HOSTS = ['localhost', '127.0.0.1']` → **PRESENTE** ✅

Ambas líneas están correctamente configuradas.

### ✅ Archivo Modificado

Claude Code confirmó que el único archivo modificado fue `./app/config/settings.py`, lo cual cumple con el criterio de aceptación de la tarea que especifica:

> "Verificar que ambas líneas estén presentes
> Archivos esperados: `./app/config/settings.py`"

### ✅ Alineación con Requirements

La tarea 3.6 referencia: `_Requirements: 1.5_`

**Requirement 1.5 (del requirements.md):**

> "THE Django_App SHALL incluir en `INSTALLED_APPS` las apps por defecto de Django: `django.contrib.admin`, `django.contrib.auth`, `django.contrib.contenttypes`, `django.contrib.sessions`, `django.contrib.messages`, `django.contrib.staticfiles`."

**Nota:** El Requirement 1.5 referenciado en la tarea 3.6 parece ser un error de mapeo en tasks.md, ya que el criterio de aceptación de la tarea habla de `DEBUG` y `ALLOWED_HOSTS`, no de `INSTALLED_APPS`. Sin embargo, las apps por defecto ya están presentes en `INSTALLED_APPS` (líneas 40-47 de settings.py), por lo que ese requirement también está cumplido.

La configuración de `DEBUG = True` y `ALLOWED_HOSTS` es necesaria para que Django funcione correctamente en desarrollo local (puerto 8000 con runserver), lo cual es un prerequisito implícito para todas las tareas de validación manual posteriores.

### ✅ Coherencia con Design.md

El design.md del spec no especifica detalles de `ALLOWED_HOSTS` o `DEBUG`, pero estos son valores estándar de configuración Django que permiten el acceso en desarrollo local. Están alineados con las restricciones del proyecto que indican ejecución local en MVP 1 (ver product.md: "Corre localmente. No se asume preparado para 20.000 usuarios").

---

## Verificación Manual

Confirmé revisando `./app/config/settings.py` (líneas 31-33):

```python
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

Ambas configuraciones están presentes y correctas.

---

## Conclusión

**Veredicto:** ✅ **COMPLETED**

La tarea 3.6 cumple todos sus criterios de aceptación:

1. ✅ `DEBUG = True` presente en settings.py
2. ✅ `ALLOWED_HOSTS = ['localhost', '127.0.0.1']` presente en settings.py
3. ✅ Único archivo modificado: ./app/config/settings.py

La tarea puede marcarse como **completed** en tasks.md.

---

## Próximo Paso

Continuar con la **Tarea 4.1**: Crear core/urls.py con rutas de autenticación.
