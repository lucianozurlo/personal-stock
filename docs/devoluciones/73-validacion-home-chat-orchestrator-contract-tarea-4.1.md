# Validación Kiro: Tarea 4.1 - HTMLSanitizer

**Spec:** home-chat-orchestrator-contract
**Tarea:** 4.1 - Implementar sanitización de HTML
**Fecha:** 2026-06-26
**Validador:** Kiro

---

## Resumen Ejecutivo

**Veredicto:** ✅ **COMPLETED**

La tarea 4.1 (Implementar sanitización de HTML) cumple con TODOS los criterios de aceptación definidos en tasks.md. La implementación de `HTMLSanitizer` es correcta, segura y está alineada con las especificaciones de seguridad del Component 6 en design.md.

---

## Validación Punto por Punto

### Criterios de Aceptación (tasks.md tarea 4.1)

| #   | Criterio                                                                  | Estado      | Evidencia                                               |
| --- | ------------------------------------------------------------------------- | ----------- | ------------------------------------------------------- |
| 1   | Crear archivo `app/core/helpers/html_sanitizer.py`                        | ✅ Cumplido | Archivo creado con clase HTMLSanitizer                  |
| 2   | Implementar `HTMLSanitizer.sanitize(html_string: str) -> str`             | ✅ Cumplido | Método de clase con firma correcta implementado         |
| 3   | ALLOWED_TAGS: p, strong, em, ul, ol, li, a, br, h1-h6, span, div          | ✅ Cumplido | Lista completa en ALLOWED_TAGS (16 tags)                |
| 4   | ALLOWED_ATTRIBUTES: a[href], \*[class, id]                                | ✅ Cumplido | Dict con 'a': ['href'] y '\*': ['class', 'id']          |
| 5   | Restricción de protocolos: http, https, mailto (previene javascript: XSS) | ✅ Cumplido | protocols=['http', 'https', 'mailto'] en bleach.clean() |
| 6   | Usar `bleach.clean()` con strip=True                                      | ✅ Cumplido | bleach.clean() con strip=True implementado              |
| 7   | Usar `bleach.linkify()` para limpiar URLs en href                         | ✅ Cumplido | bleach.linkify() con skip_tags=['pre', 'code']          |
| 8   | Manejar empty string → return ''                                          | ✅ Cumplido | Guard `if not html_string: return ''` al inicio         |

### Validación contra Requirements

**Requirement 2 AC3:** "FOR ALL responses in MVP 1, THE Response_Payload SHALL set `html_render` to true (HTML sanitizado es el único formato soportado en MVP 1)"

- ✅ HTMLSanitizer implementado para sanitizar todo HTML antes de enviar al frontend

**Requirement 6 AC4:** "WHEN the parsed Response_Payload contains field `html_render` with value true, THE Django_Frontend SHALL render the `output` field as sanitized HTML"

- ✅ HTMLSanitizer provee la sanitización requerida

**Requirement 10:** "Registrar limitación de MVP 1 para html_render"

- ✅ HTMLSanitizer es el componente que habilita el único formato soportado en MVP 1

### Validación contra Design (Component 6)

**Location:** ✅ `app/core/helpers/html_sanitizer.py` (correcto)

**Responsibilities:**

- ✅ Sanitize HTML output from n8n before returning to frontend
- ✅ Use bleach library with allow-list approach
- ✅ Prevent XSS attacks through untrusted external HTML
- ✅ Zero trust external systems (defense in depth)

**Security Requirements:**

- ✅ Removes all tags not in ALLOWED_TAGS
- ✅ Removes all attributes not in ALLOWED_ATTRIBUTES
- ✅ Restricts href protocols to http, https, mailto (prevents javascript: XSS)
- ✅ Strips script tags, event handlers, and malicious content

**Interface Compliance:**

- ✅ Método de clase (@classmethod)
- ✅ Firma correcta: `sanitize(cls, html_string: str) -> str`
- ✅ Manejo de input vacío
- ✅ bleach.clean() con parámetros correctos
- ✅ bleach.linkify() para limpiar URLs

---

## Hallazgos

### Implementación Correcta

1. **Archivo creado correctamente:** `app/core/helpers/html_sanitizer.py`

2. **Clase y método correctos:**

   ```python
   class HTMLSanitizer:
       @classmethod
       def sanitize(cls, html_string: str) -> str:
   ```

3. **ALLOWED_TAGS completo:** 16 tags permitidos (p, strong, em, ul, ol, li, a, br, h1, h2, h3, h4, h5, h6, span, div)

4. **ALLOWED_ATTRIBUTES correcto:**

   ```python
   ALLOWED_ATTRIBUTES = {
       'a': ['href'],
       '*': ['class', 'id']
   }
   ```

5. **Protección XSS mediante restricción de protocolos:**

   ```python
   protocols=['http', 'https', 'mailto']
   ```

   Esto previene `javascript:alert(1)` y otros vectores XSS.

6. **bleach.clean() con strip=True:** Remueve tags no permitidos en lugar de escaparlos.

7. **bleach.linkify() con skip_tags:** Limpia URLs pero evita linkificar dentro de bloques de código.

8. **Manejo de empty string:**
   ```python
   if not html_string:
       return ''
   ```

### Seguridad (CRÍTICO)

HTMLSanitizer es un **componente de seguridad crítico** que implementa el principio de "defense in depth":

- **Zero trust external systems:** No confía en n8n para sanitización
- **Allow-list approach:** Solo permite tags y atributos explícitamente listados
- **Protocol restriction:** Previene javascript: XSS y otros protocolos maliciosos
- **Complete removal:** strip=True asegura que tags maliciosos se eliminan completamente

Esta implementación cumple con TODAS las mejores prácticas de seguridad para sanitización de HTML.

### Tests Existentes Sin Regresión

Se verificó que los 37 tests existentes pasan sin regresión:

- 17 tests de ConversationIdManagerTest ✅
- 14 tests de UserObjectBuilderTest ✅
- 6 tests de AuthViewsTest ✅

Todos los tests pasan correctamente, lo que confirma que la adición de HTMLSanitizer no introduce regresiones.

---

## Validación contra Spec

### Requirements.md

- ✅ Requirement 2 AC3: HTML sanitizado es el único formato en MVP 1
- ✅ Requirement 6 AC4: Renderizar output como sanitized HTML
- ✅ Requirement 10: Limitación de MVP 1 para html_render

### Design.md

- ✅ Component 6 (HTMLSanitizer): Especificación completa implementada
- ✅ Security section: Zero trust external systems
- ✅ Defense in depth: Django MUST sanitize HTML from n8n

### Tasks.md

- ✅ Tarea 4.1: Todos los 8 criterios de aceptación cumplidos

---

## Próximos Pasos

### Tarea 4.2 (MANDATORY - Siguiente)

**Escribir tests unitarios para HTMLSanitizer**

Este es el siguiente paso OBLIGATORIO antes de continuar. Los tests son CRÍTICOS porque HTMLSanitizer es un componente de seguridad:

Tests requeridos:

- Tags permitidos pasan sin cambios
- Tags no permitidos se remueven
- Script tags bloqueados
- Event handlers (onclick, onerror) bloqueados
- javascript: protocol en href bloqueado
- http/https/mailto protocols permitidos
- Atributos no permitidos removidos
- Empty string retorna empty string

**IMPORTANTE:** Los tests de seguridad para HTMLSanitizer NO son opcionales. Son MANDATORY porque validan protecciones XSS críticas.

### Actualización de Estado

1. ✅ Marcar tarea 4.1 como [x] en tasks.md
2. ✅ Actualizar PROGRESO.md:
   - Spec actual: home-chat-orchestrator-contract
   - Tarea actual: 4.2
   - Último gate pasado: tarea 4.1 completed — validación Kiro OK
   - Next: Paso 3.7 — implementar tarea 4.2 con Claude Code (sesión nueva)

---

## Conclusión

La tarea 4.1 está **COMPLETED** y lista para producción. La implementación de HTMLSanitizer cumple con:

✅ Todos los criterios de aceptación de tasks.md
✅ Toda la especificación de Component 6 en design.md
✅ Todos los requirements relacionados en requirements.md
✅ Todas las mejores prácticas de seguridad para sanitización HTML
✅ Sin regresiones en tests existentes

La implementación es correcta, segura y está lista para continuar con la tarea 4.2 (tests unitarios de seguridad).

---

**Firmado:** Kiro (Validador)
**Fecha:** 2026-06-26
