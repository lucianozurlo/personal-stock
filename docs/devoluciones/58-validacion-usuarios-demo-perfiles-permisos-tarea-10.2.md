# Validación tarea 10.2 — usuarios-demo-perfiles-permisos

## Qué se implementó

Tarea 10.2: Actualizar template `home.html` para mostrar perfil del usuario actual y sus roles (condicionalmente si el perfil es Usuario IC).

## Cambios realizados

**Archivo modificado:** `templates/home.html`

### Cambio 1 — Dropdown de usuario (líneas 101-103)

Dentro del bloque `.dd-head > div`, después del `<small>` con el email, se agregaron dos líneas:

- `<small>{{ perfil }}</small>` — muestra el perfil siempre (visible para cualquier usuario)
- `{% if perfil == 'Usuario IC' and roles %}<small>{{ r.name }}, ...</small>{% endif %}` — muestra los roles solo si el perfil es "Usuario IC" y tiene al menos un rol asignado

Reutiliza el estilo `.dd-head small` existente (`color: var(--text-3)`, `font-size: 12px`) sin CSS nuevo.

### Cambio 2 — window.PS_USER (líneas 223-229)

Se extendió el objeto JS con:

- `perfil: "{{ perfil|escapejs }}"` — expone el perfil al frontend
- `roles: [...]` — lista de nombres de roles como array JSON, usando `ps_user_data.roles` (lista de strings ya preparada en views.py por tarea 10.1)

## Criterios de aceptación verificados

### Criterio: Agregar sección visible que muestre perfil del usuario actual

- Estado: **Sí**
- Evidencia: `templates/home.html` línea 102 → `<small>{{ perfil }}</small>` dentro de `.dd-head`. Renderizado visible en el dropdown de usuario, usando estilos muted existentes.

### Criterio: Agregar sección que muestre roles (si perfil == Usuario IC)

- Estado: **Sí**
- Evidencia: `templates/home.html` línea 103 → `{% if perfil == 'Usuario IC' and roles %}<small>{% for r in roles %}{{ r.name }}...{% endfor %}</small>{% endif %}`. Solo aparece si el perfil es exactamente "Usuario IC" y hay roles asignados.

### Criterio: Mantener diseño consistente con template existente

- Estado: **Sí**
- Evidencia: No se agregó CSS nuevo. La sección reutiliza `.dd-head small` (ya definida en `templates/css/styles.css` línea 1363). Misma paleta de color y tipografía que el email.

### Criterio: Requirements 9.3, 3.4 — Exponer perfil/roles al contexto de Django views y al frontend JS

- Estado: **Sí**
- Evidencia: `window.PS_USER` extendido con `perfil` y `roles` en `templates/home.html` líneas 225-226. Usa `ps_user_data` del contexto ya preparado por tarea 10.1 en `app/core/views.py`.

## Tests

```
Ran 38 tests in 509.067s — OK
```

Sin regresiones. Suite completa pasa.

## Fecha / Spec / Tarea

- **Fecha:** 2026-06-23
- **Spec:** usuarios-demo-perfiles-permisos
- **Tarea:** 10.2
- **Veredicto:** ✅ **COMPLETED**

## Hallazgos de validación Kiro

### Validación contra requirements.md

**Requirement 9 (Exponer Perfil y Roles al Sistema de Autenticación):**

- ✅ AC 9.3: Profile y roles expuestos a través de user context en Django views — verificado en views.py líneas 34-35
- ✅ AC 3.4 (Requirement 3): Profile expuesto al sistema de autenticación — verificado en template home.html líneas 102-103 y 227-228

**Evidencia técnica verificada:**

1. **Template home.html línea 102:** `<small>{{ perfil }}</small>` — perfil visible en dropdown usuario
2. **Template home.html línea 103:** `{% if perfil == 'Usuario IC' and roles %}<small>{% for r in roles %}{{ r.name }}{% if not forloop.last %}, {% endif %}{% endfor %}</small>{% endif %}` — roles condicionales con lógica correcta
3. **styles.css línea 1363:** `.dd-head small` ya existente, reutilizado sin crear CSS nuevo
4. **Template home.html líneas 227-228:** `window.PS_USER` extendido con `perfil: "{{ perfil|escapejs }}"` y `roles: [...]`
5. **Tests:** 38/38 OK sin regresiones (579.002s)

### Decisión

La tarea 10.2 cumple todos los criterios de aceptación del spec:

- ✅ Sección visible con perfil del usuario actual
- ✅ Sección condicional con roles (solo Usuario IC)
- ✅ Diseño consistente (reutiliza estilos existentes)
- ✅ Exposición a contexto JS (window.PS_USER)
- ✅ Tests completos sin regresiones

**Marcada como [x] en tasks.md línea 320.**
