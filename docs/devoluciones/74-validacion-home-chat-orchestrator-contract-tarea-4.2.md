# Validación: home-chat-orchestrator-contract — Tarea 4.2

**Fecha:** 2026-06-26
**Spec:** home-chat-orchestrator-contract
**Tarea:** 4.2 — Escribir tests unitarios para HTMLSanitizer
**Estado reportado:** READY FOR VALIDATION
**Validador:** Kiro
**Veredicto:** ✅ **COMPLETED**

---

## Qué se implementó

Se agregó la clase `HTMLSanitizerTest` a `app/core/tests.py`, siguiendo el patrón
establecido por las tareas 2.3 y 3.2 (archivo único, no directorio `tests/`).

Se agregó el import:

```python
from core.helpers.html_sanitizer import HTMLSanitizer
```

Se implementaron 12 tests cubriendo todos los criterios de la tarea, incluyendo
3 tests críticos de seguridad XSS (script, onclick/onerror, javascript:).

---

## Criterios vs. evidencia

| Criterio (tasks.md 4.2)                            | Estado | Evidencia                                                                                        |
| -------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------ |
| Test: tags permitidos pasan sin cambios            | ✅     | `test_allowed_tags_pass_through` — ok                                                            |
| Test: tags no permitidos se remueven               | ✅     | `test_disallowed_tags_stripped_content_kept` — ok                                                |
| Test: script tags bloqueados                       | ✅     | `test_script_tags_blocked` — ok                                                                  |
| Test: event handlers (onclick, onerror) bloqueados | ✅     | `test_onclick_event_handler_blocked`, `test_onerror_event_handler_blocked` — ok                  |
| Test: javascript: protocol en href bloqueado       | ✅     | `test_javascript_protocol_href_blocked` — ok                                                     |
| Test: http/https/mailto protocols permitidos       | ✅     | `test_https_protocol_allowed`, `test_http_protocol_allowed`, `test_mailto_protocol_allowed` — ok |
| Test: atributos no permitidos removidos            | ✅     | `test_disallowed_attribute_style_removed`, `test_allowed_class_attribute_kept` — ok              |
| Test: empty string retorna empty string            | ✅     | `test_empty_string_returns_empty` — ok                                                           |

**Todos los criterios de aceptación cumplidos.**

---

## Resultado de ejecución validada por Kiro

```bash
$ python3 manage.py test core.tests.HTMLSanitizerTest
Found 12 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
............
----------------------------------------------------------------------
Ran 12 tests in 0.028s

OK
Destroying test database for alias 'default'...
```

✅ **Todos los tests pasan exitosamente.**

---

## Validación contra requirements.md

### Design - Component 6 (HTMLSanitizer)

**Especificación:**

- ALLOWED_TAGS: p, strong, em, ul, ol, li, a, br, h1-h6, span, div
- ALLOWED_ATTRIBUTES: a[href], \*[class, id]
- Restricción de protocolos: http, https, mailto (previene javascript: XSS)
- Usar bleach.clean() con strip=True
- Usar bleach.linkify() para limpiar URLs en href
- Manejar empty string → return ''

**Implementación validada:**

```python
class HTMLSanitizer:
    ALLOWED_TAGS = [
        'p', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'br',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div'
    ]
    ALLOWED_ATTRIBUTES = {
        'a': ['href'],
        '*': ['class', 'id']
    }

    @classmethod
    def sanitize(cls, html_string: str) -> str:
        if not html_string:
            return ''
        cleaned = bleach.clean(
            html_string,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            protocols=['http', 'https', 'mailto'],
            strip=True
        )
        cleaned = bleach.linkify(cleaned, skip_tags=['pre', 'code'])
        return cleaned
```

✅ **Implementación coincide 100% con especificación de requirements.md.**

### Design - Testing Strategy

**tasks.md especifica 8 tests obligatorios; implementación tiene 12 tests** (cobertura superior):

1. ✅ Tags permitidos pasan sin cambios
2. ✅ Tags no permitidos se remueven
3. ✅ Script tags bloqueados (crítico XSS)
4. ✅ Event handlers bloqueados (2 tests: onclick y onerror)
5. ✅ javascript: protocol bloqueado (crítico XSS)
6. ✅ http/https/mailto protocols permitidos (3 tests: uno por protocol)
7. ✅ Atributos no permitidos removidos (2 tests: style removido, class permitido)
8. ✅ Empty string retorna empty string

**Cobertura de seguridad XSS — CRÍTICA para este componente:**

- ✅ Script injection bloqueado
- ✅ Event handler injection bloqueado
- ✅ Protocol injection (javascript:) bloqueado
- ✅ Solo protocols seguros permitidos (http, https, mailto)

---

## Archivos modificados

- `app/core/tests.py` — agregado import `HTMLSanitizer` y clase `HTMLSanitizerTest` (líneas 1033–1146)

---

## Notas técnicas

- **bleach 6.1.0**: `linkify()` agrega `rel="nofollow"` a links http/https. Los tests
  usan `assertIn()` (no exact match) para ser resilientes a este comportamiento.
- **Script tags**: `<script>alert("xss")</script>` → bleach elimina los tags pero el texto queda.
  El test valida ausencia de `<script>` y `</script>`, que es la protección real.
- **javascript: protocol**: bleach limpia el href, el `<a>` queda sin href:
  `<a>Click here</a>`. Test valida `assertNotIn('javascript:', result)`.
- **Patrón de archivo único**: tasks.md especifica crear `app/core/tests/test_html_sanitizer.py`,
  pero las tareas 2.3 y 3.2 establecieron el patrón de archivo único `tests.py`.
  Se siguió el patrón existente por consistencia.

---

## Veredicto final

✅ **Tarea 4.2 COMPLETED**

**Justificación:**

1. Todos los criterios de aceptación de tasks.md cumplidos (8/8)
2. Implementación cumple 100% con especificación de requirements.md
3. Todos los tests pasan exitosamente (12/12 OK)
4. Cobertura de seguridad XSS completa (crítica para este componente)
5. Patrón de implementación consistente con tareas anteriores (2.3, 3.2)

**Próximos pasos:**

- Marcar tarea 4.2 como [x] completed en tasks.md
- Actualizar PROGRESO.md indicando próxima tarea: 5.1
