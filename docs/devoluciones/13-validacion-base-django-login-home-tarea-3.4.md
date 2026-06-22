# Validación: base-django-login-home - Tarea 3.4

**Fecha:** 2026-06-21
**Spec:** `base-django-login-home`
**Tarea:** 3.4 - Configurar STATICFILES_DIRS para assets en ./templates
**Validador:** Kiro (orchestrator)

---

## Contexto

Claude Code reportó la finalización de la tarea 3.4, que consiste en agregar la configuración de `STATICFILES_DIRS` en `settings.py` para que Django pueda servir los assets (CSS, JS, imágenes) desde las carpetas fuente en `./templates`.

---

## Criterios de aceptación (según tasks.md)

| Criterio | Descripción                                                                      |
| -------- | -------------------------------------------------------------------------------- |
| 1        | Agregar `STATIC_ROOT = BASE_DIR / 'staticfiles'` después del bloque `STATIC_URL` |
| 2        | Agregar `STATICFILES_DIRS` con las 3 rutas: `css`, `js`, `img`                   |
| 3        | Verificar con `grep "STATICFILES_DIRS"` que las 3 rutas están presentes          |
| 4        | Único archivo modificado: `./app/config/settings.py`                             |

---

## Evidencia revisada

### 1. Archivo modificado: `./app/config/settings.py`

**Líneas 125-131:**

```python
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR.parent / 'templates' / 'css',
    BASE_DIR.parent / 'templates' / 'js',
    BASE_DIR.parent / 'templates' / 'img',
]
```

### 2. Validación de criterios

| Criterio                      | Estado    | Hallazgo                                              |
| ----------------------------- | --------- | ----------------------------------------------------- |
| STATIC_ROOT definido          | ✅ CUMPLE | Línea 126: `STATIC_ROOT = BASE_DIR / 'staticfiles'`   |
| STATICFILES_DIRS con ruta css | ✅ CUMPLE | Línea 128: `BASE_DIR.parent / 'templates' / 'css'`    |
| STATICFILES_DIRS con ruta js  | ✅ CUMPLE | Línea 129: `BASE_DIR.parent / 'templates' / 'js'`     |
| STATICFILES_DIRS con ruta img | ✅ CUMPLE | Línea 130: `BASE_DIR.parent / 'templates' / 'img'`    |
| Verificación grep             | ✅ CUMPLE | Claude Code confirmó output del grep (líneas 126-129) |
| Único archivo modificado      | ✅ CUMPLE | Solo `./app/config/settings.py` fue tocado            |

---

## Validación contra requirements.md

### Requirement 3: Configuración de archivos estáticos

**Criterio 3.1:**

> WHEN se configura `STATICFILES_DIRS` en `settings.py`, THE Django_App SHALL incluir las rutas absolutas: `BASE_DIR.parent / 'templates' / 'css'`, `BASE_DIR.parent / 'templates' / 'js'`, `BASE_DIR.parent / 'templates' / 'img'`

**Resultado:** ✅ **CUMPLE** — Las 3 rutas están correctamente configuradas con la sintaxis de pathlib usando `BASE_DIR.parent / 'templates' / <subdirectorio>`.

**Nota sobre otros criterios del Requirement 3:**
Los criterios 3.2, 3.3, 3.4 de requirements.md requieren:

- Ejecutar `python manage.py collectstatic`
- Resolver correctamente `{% static 'css/styles.css' %}`
- Resolver correctamente `{% static 'img/personal-stock-logo.svg' %}`

Estos criterios se validarán en tareas posteriores (verificación manual en tarea 10 y tests en tarea 11.2). La tarea 3.4 se enfoca únicamente en la **configuración declarativa** de `STATICFILES_DIRS`, lo cual está completo.

---

## Verificación de estructura de rutas

**Rutas esperadas según structure.md:**

```
/Users/luciano/Desktop/PS-edit/
  app/
    config/
      settings.py
  templates/
    css/
    js/
    img/
```

**Rutas configuradas:**

- `BASE_DIR` = `/Users/luciano/Desktop/PS-edit/app`
- `BASE_DIR.parent` = `/Users/luciano/Desktop/PS-edit`
- `BASE_DIR.parent / 'templates' / 'css'` = `/Users/luciano/Desktop/PS-edit/templates/css` ✅
- `BASE_DIR.parent / 'templates' / 'js'` = `/Users/luciano/Desktop/PS-edit/templates/js` ✅
- `BASE_DIR.parent / 'templates' / 'img'` = `/Users/luciano/Desktop/PS-edit/templates/img` ✅

**Conclusión:** La estructura de rutas es coherente con `structure.md`.

---

## Hallazgos

### ✅ Cumple especificación

1. **Configuración correcta de STATIC_ROOT:** Django podrá recolectar archivos estáticos en `./app/staticfiles/` cuando se ejecute `collectstatic`.

2. **Configuración correcta de STATICFILES_DIRS:** Las 3 rutas apuntan correctamente a las carpetas fuente en `./templates`, usando `BASE_DIR.parent` para subir un nivel desde `./app`.

3. **Sintaxis pathlib correcta:** Se usa el operador `/` para concatenar rutas, consistente con el resto de `settings.py` (ej: `BASE_DIR / 'staticfiles'`).

4. **Único archivo modificado:** Se respeta la restricción de modificar solo `settings.py`.

### 📋 Sin observaciones

No se detectaron inconsistencias, desviaciones ni configuraciones faltantes.

---

## Veredicto

**✅ COMPLETED**

La tarea 3.4 cumple:

- Todos los criterios de aceptación definidos en `tasks.md`
- El Requirement 3.1 de `requirements.md`
- La política de estructura de `structure.md`
- La restricción de modificar un único archivo

**Acción requerida:** Marcar la tarea 3.4 como `[x]` en `tasks.md` y proceder con la tarea 3.5 (configurar sesiones persistentes).

---

## Notas adicionales

- La validación funcional de `collectstatic` y resolución de `{% static %}` se ejecutará en tarea 10 (verificación manual) y tarea 11.2 (tests unitarios).
- No se requieren correcciones ni cambios adicionales en esta tarea.
- Claude Code siguió correctamente la disciplina de una tarea por sesión en modo plan.
