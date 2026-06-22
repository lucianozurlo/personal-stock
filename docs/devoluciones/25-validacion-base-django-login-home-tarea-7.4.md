# Validación: base-django-login-home :: Tarea 7.4

## Metadatos

- **Spec:** base-django-login-home
- **Tarea:** 7.4 - Integrar home.html con Django - parte 3 (inyectar window.PS_USER)
- **Fecha de validación:** 2026-06-22
- **Validador:** Kiro (Orchestrator Agent)
- **Implementador:** Claude Code

---

## Criterios de aceptación (según tasks.md)

| #   | Criterio                                                       | Estado  | Evidencia                                                              |
| --- | -------------------------------------------------------------- | ------- | ---------------------------------------------------------------------- |
| 1   | Bloque `window.PS_USER = {...}` existe en home.html            | ✅ PASS | Líneas 220-226 de `/Users/luciano/Desktop/PS-edit/templates/home.html` |
| 2   | Aparece ANTES de `<script src="{% static 'js/app.js' %}">`     | ✅ PASS | PS_USER línea 220 < app.js línea 227                                   |
| 3   | `firstName` usa `{{ user.first_name\|default:user.username }}` | ✅ PASS | home.html:222                                                          |
| 4   | `username` usa `{{ user.username }}`                           | ✅ PASS | home.html:223                                                          |
| 5   | `email` usa `{{ user.email }}`                                 | ✅ PASS | home.html:224                                                          |

---

## Requirements cumplidos

- **Requirement 8.1:** "WHEN el template `home.html` se renderiza, THE Django_App SHALL inyectar una variable JavaScript `window.PS_USER` conteniendo `{ firstName: "{{ user.first_name }}", username: "{{ user.username }}" }` en un bloque `<script>` inline antes de cargar `app.js`."
  - **Resultado:** ✅ CUMPLIDO

---

## Hallazgos

### ✅ Implementación correcta

1. **Bloque inline presente:**

   ```javascript
   <script>
     window.PS_USER = {
       firstName: "{{ user.first_name|default:user.username }}",
       username: "{{ user.username }}",
       email: "{{ user.email }}"
     };
   </script>
   ```

   - Ubicación: líneas 220-226
   - Formato: correcto
   - Indentación: consistente con el resto del HTML

2. **Orden de ejecución garantizado:**
   - `window.PS_USER` se define en línea 220
   - `app.js` se carga en línea 227
   - Esto asegura que `window.PS_USER` está disponible cuando `app.js` se ejecuta

3. **Uso de filtro `default` (mejora sobre spec):**
   - El campo `firstName` usa `{{ user.first_name|default:user.username }}`
   - Esto garantiza que siempre habrá un valor, incluso si `first_name` está vacío
   - **Verificación contra Requirement 7.4:** "WHEN un usuario sin `first_name` definido accede a `/`, THE Django_App SHALL renderizar `<span id="welcomeTitle">Hola, {{ user.username }}.</span>` como fallback."
   - La implementación es consistente con el fallback ya implementado en tarea 7.3

4. **Campo adicional `email` incluido:**
   - Requirement 8.1 especifica `firstName` y `username`
   - La implementación agrega también `email`
   - Esto es una **mejora aceptable** porque:
     - No rompe ningún requirement
     - El campo `email` ya está disponible en `request.user`
     - Puede ser útil para funcionalidades futuras de `app.js`
     - No hay restricción explícita contra incluir campos adicionales

### 🟡 Observaciones menores (no bloquean el completed)

1. **Requirement 8.1 menciona estructura `{ firstName: "...", username: "..." }`:**
   - La implementación agrega `email` como tercer campo
   - **Veredicto:** NO es una desviación crítica — los campos requeridos están presentes y el campo adicional no genera conflicto

---

## Verificación contra requirements.md

### Requirement 8.1 (extraído de requirements.md)

> **Acceptance Criteria:**
>
> 1. WHEN el template `home.html` se renderiza, THE Django_App SHALL inyectar una variable JavaScript `window.PS_USER` conteniendo `{ firstName: "{{ user.first_name }}", username: "{{ user.username }}" }` en un bloque `<script>` inline antes de cargar `app.js`.

**Estado:** ✅ CUMPLIDO

**Evidencia:**

- Bloque inline existe (líneas 220-226)
- Campos `firstName` y `username` presentes con los template tags correctos
- Orden correcto: inline script antes de `<script src="{% static 'js/app.js' %}">`

---

## Compatibilidad con tareas dependientes

### Tarea 8.1 (siguiente en el plan)

**Objetivo:** Reemplazar "Benja" en `app.js` - parte 1 (RANDOM_GREETINGS)

**Dependencia de 7.4:**

- La tarea 8.1 requiere que `window.PS_USER` esté disponible
- La tarea 7.4 garantiza que `window.PS_USER` se define antes de ejecutar `app.js`
- **Veredicto:** ✅ La dependencia está satisfecha

### Tarea 8.3 (validación de PS_USER)

**Objetivo:** Agregar validación de `PS_USER` en `app.js`

**Código esperado:**

```javascript
if (!window.PS_USER || !window.PS_USER.firstName) {
  console.error("PS_USER no está definido. El usuario debe estar autenticado.");
  window.location.href = "/login/";
}
```

**Compatibilidad:**

- La tarea 7.4 garantiza que `window.PS_USER.firstName` siempre tendrá un valor (por el uso de `|default:user.username`)
- La validación en 8.3 detectará correctamente si `window.PS_USER` no se inyectó por algún error de template
- **Veredicto:** ✅ Compatible

---

## Pruebas recomendadas (para verificación manual en tarea 10)

Cuando llegue a la tarea 10 (Verificación manual del flujo completo), validar:

1. **Usuario con `first_name` definido:**
   - Abrir consola del navegador en `/`
   - Ejecutar: `console.log(window.PS_USER)`
   - Verificar que `firstName` contiene el valor de `user.first_name`

2. **Usuario sin `first_name` (solo username):**
   - Crear usuario de prueba sin `first_name`
   - Login y verificar que `window.PS_USER.firstName` contiene `user.username`

3. **Script se ejecuta antes de app.js:**
   - Abrir DevTools → Sources
   - Verificar que el inline script aparece antes de `app.js` en el HTML

---

## Veredicto final

### ✅ TAREA 7.4 → **COMPLETED**

**Razones:**

1. ✅ **Todos los criterios de aceptación cumplidos:**
   - Bloque `window.PS_USER` existe
   - Orden correcto (antes de `app.js`)
   - Campos `firstName`, `username`, `email` correctamente inyectados con template tags

2. ✅ **Requirement 8.1 satisfecho:**
   - La variable JavaScript `window.PS_USER` se inyecta inline antes de cargar `app.js`
   - Los campos requeridos (`firstName`, `username`) están presentes
   - El campo adicional (`email`) no genera conflicto

3. ✅ **Implementación robusta:**
   - Uso de filtro `default` garantiza fallback coherente con tarea 7.3
   - Formato correcto y bien indentado

4. ✅ **Compatible con tareas dependientes:**
   - Tarea 8.1, 8.2, 8.3 pueden proceder sin bloqueos

**Archivos modificados:**

- `/Users/luciano/Desktop/PS-edit/templates/home.html` (+7 líneas)

**Líneas afectadas:**

- 220-226 (nuevo bloque inline)

---

## Próxima tarea

### Tarea 8.1: Reemplazar "Benja" en app.js - parte 1 (RANDOM_GREETINGS)

**Prerequisitos cumplidos:**

- ✅ `window.PS_USER` disponible (tarea 7.4)
- ✅ Templates integrados con Django (tareas 7.1, 7.2, 7.3, 7.4)

**Archivos a modificar:**

- `/Users/luciano/Desktop/PS-edit/templates/js/app.js`

**Objetivo:**

- Reemplazar todas las ocurrencias de `"Benja"` en `RANDOM_GREETINGS` por `${window.PS_USER.firstName}` usando template literals

---

## Firma

**Validador:** Kiro (Spec Workflow Orchestrator Agent)
**Fecha:** 2026-06-22
**Spec:** base-django-login-home
**Tarea validada:** 7.4
**Estado:** ✅ COMPLETED
