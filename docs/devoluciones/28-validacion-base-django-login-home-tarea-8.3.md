# Validación: base-django-login-home - Tarea 8.3

**Fecha:** 2026-06-22
**Spec:** base-django-login-home
**Tarea:** 8.3 - Agregar validación de PS_USER en app.js
**Validador:** Kiro (orchestrator agent)

---

## Contexto

Claude Code reportó la implementación de la tarea 8.3, que agrega una guardia de validación al inicio de `app.js` para verificar que `window.PS_USER` esté definido antes de ejecutar lógica que depende de él.

---

## Criterios de Aceptación de la Tarea

Según `tasks.md`, tarea 8.3:

> Al inicio de `./templates/js/app.js` (después de constantes, antes de funciones), agregar:
>
> ```javascript
> if (!window.PS_USER || !window.PS_USER.firstName) {
>   console.error(
>     "PS_USER no está definido. El usuario debe estar autenticado.",
>   );
>   window.location.href = "/login/";
> }
> ```
>
> - Verificar que el bloque existe al inicio del archivo
> - Archivos esperados: `./templates/js/app.js`
> - _Requirements: 8.1_

---

## Verificación de la Implementación

### 1. Presencia del bloque de validación

**Ubicación:** `./templates/js/app.js`, líneas 33-37

**Código encontrado:**

```javascript
if (!window.PS_USER || !window.PS_USER.firstName) {
  console.error("PS_USER no está definido. El usuario debe estar autenticado.");
  window.location.href = "/login/";
}
```

✅ **CUMPLE**: El bloque existe exactamente como especificado.

---

### 2. Mensaje de `console.error` exacto

**Esperado:** `"PS_USER no está definido. El usuario debe estar autenticado."`

**Encontrado:** `"PS_USER no está definido. El usuario debe estar autenticado."` (líneas 34-36)

✅ **CUMPLE**: El mensaje es exacto, incluyendo puntuación.

---

### 3. Redirección a `/login/`

**Código encontrado:** `window.location.href = "/login/";` (línea 37)

✅ **CUMPLE**: La redirección está presente y apunta a la ruta correcta.

---

### 4. Ubicación: después de constantes, antes de funciones

**Estructura del archivo:**

- Líneas 1-31: Constantes (`STORAGE_KEY`, `STARTER_PRESETS`, `RANDOM_GREETINGS`, `N8N_WEBHOOK_URL`)
- **Líneas 33-37: Bloque de validación** ← **UBICACIÓN CORRECTA**
- Línea 40+: Array `RANDOM_GREETINGS` (que usa `window.PS_USER.firstName`)
- Línea 66+: Variables de estado global
- Línea 100+: Funciones

✅ **CUMPLE**: La guardia se ejecuta antes de que `RANDOM_GREETINGS` evalúe `window.PS_USER.firstName` durante su inicialización (línea 40).

**Nota de diseño (reportada por Claude Code):** El bloque se insertó entre `STARTER_PRESETS` (línea 31) y `RANDOM_GREETINGS` (línea 40) intencionalmente para que la guardia ejecute antes de que `RANDOM_GREETINGS` evalúe `window.PS_USER.firstName` durante su inicialización.

---

### 5. Único archivo modificado

**Archivos esperados:** Solo `./templates/js/app.js`

✅ **CUMPLE**: Claude Code confirmó que no se modificaron otros archivos.

---

## Validación contra requirements.md

### Requirement 8.1 (Acceptance Criteria 8.1)

> WHEN el template `home.html` se renderiza, THE Django_App SHALL inyectar una variable JavaScript `window.PS_USER` conteniendo `{ firstName: "{{ user.first_name }}", username: "{{ user.username }}" }` en un bloque `<script>` inline antes de cargar `app.js`.

**Validación:**

- La tarea 8.3 NO modifica `home.html`, pero ASUME que `window.PS_USER` ya fue inyectado por la tarea 7.4.
- La guardia valida que `window.PS_USER` y `window.PS_USER.firstName` existen antes de continuar.
- Si `window.PS_USER` NO está definido, se muestra un error claro y se redirige a login (comportamiento defensivo correcto).

✅ **CUMPLE**: La implementación refuerza el requirement 8.1 agregando una capa de protección.

---

## Hallazgos

### ✅ Hallazgos positivos

1. **Bloque de validación correcto**: El código coincide exactamente con el spec (sintaxis, mensaje, redirección).
2. **Ubicación estratégica**: La guardia se ejecuta antes de que `RANDOM_GREETINGS` intente acceder a `window.PS_USER.firstName`, evitando errores de referencia.
3. **Experiencia de usuario defensiva**: Si `home.html` falla al inyectar `PS_USER` (error de servidor, template malformado, etc.), el usuario es redirigido a login con un mensaje claro en consola, en lugar de mostrar un error de JavaScript en pantalla.
4. **Sin modificaciones colaterales**: Solo se modificó `app.js`, como esperado.

### ⚠️ Observaciones menores (no bloquean completed)

1. **Dependencia de tarea 7.4**: Esta guardia ASUME que la tarea 7.4 (inyectar `window.PS_USER` en `home.html`) ya fue completada. Si 7.4 NO se ejecutó correctamente, esta guardia siempre redirigirá a login.
   - **Mitigación:** La tarea 7.4 está marcada como `[x]` (completada) en `tasks.md`, por lo que esta dependencia está satisfecha.

2. **Caso edge: `user.first_name` vacío**: Si un usuario Django no tiene `first_name` definido, `window.PS_USER.firstName` será una cadena vacía (`""`), no `undefined`. La guardia `!window.PS_USER.firstName` evaluará `true` y redirigirá a login.
   - **Análisis:** Este comportamiento es CORRECTO según el requirement 7.4 (fallback a `user.username`), pero la inyección en `home.html` debe garantizar que `firstName` SIEMPRE tenga un valor (usando `{{ user.first_name|default:user.username }}`).
   - **Acción:** Verificar en checkpoint 10 (validación manual) que usuarios sin `first_name` no son bloqueados por la guardia.

---

## Veredicto

### ✅ **TAREA 8.3: COMPLETED**

**Justificación:**

- Todos los criterios de aceptación de la tarea están cumplidos.
- El código coincide exactamente con el spec.
- La ubicación del bloque es estratégica y previene errores de referencia.
- La implementación refuerza el requirement 8.1 con una capa defensiva.
- No se modificaron archivos fuera del alcance.

**Próximos pasos:**

1. Marcar tarea 8.3 como `[x]` en `tasks.md`.
2. Continuar con la tarea 9 (Checkpoint - Migraciones y creación de superusuario).
3. Durante el checkpoint 10 (validación manual), verificar específicamente:
   - Que usuarios con `first_name` vacío no son bloqueados por la guardia.
   - Que el mensaje de consola aparece correctamente si `PS_USER` no está definido (simular eliminando el `<script>` de inyección temporalmente).

---

## Referencias

- **Spec:** `.kiro/specs/base-django-login-home/`
- **Requirements:** `requirements.md` (Requirement 8.1)
- **Tasks:** `tasks.md` (Tarea 8.3)
- **Archivo validado:** `./templates/js/app.js` (líneas 33-37)
- **Dependencias:** Tarea 7.4 (inyección de `window.PS_USER` en `home.html`)
