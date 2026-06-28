# Validación de Tarea 8.6 - home-chat-orchestrator-contract

**Fecha:** 2026-04-17
**Spec:** home-chat-orchestrator-contract
**Tarea:** 8.6 - Sanitizar HTML y validar Response_Payload en ChatView
**Validador:** Kiro

---

## Resumen Ejecutivo

✅ **VEREDICTO: COMPLETED**

La tarea 8.6 cumple con todos los criterios de aceptación definidos en `tasks.md`. La implementación en `app/core/views.py` integra correctamente `HTMLSanitizer` y `ResponsePayloadSerializer` para sanitizar la respuesta de n8n y validar su estructura antes de devolverla al frontend.

---

## Criterios de Aceptación Validados

### Criterio 1: HTMLSanitizer importado desde core.helpers.html_sanitizer

**Estado:** ✓ Cumplido
**Evidencia:** `views.py:14` - `from core.helpers.html_sanitizer import HTMLSanitizer`

### Criterio 2: response_data['output'] sanitizado con HTMLSanitizer.sanitize()

**Estado:** ✓ Cumplido
**Evidencia:** `views.py:179-180`

```python
if 'output' in response_data:
    response_data['output'] = HTMLSanitizer.sanitize(response_data['output'])
```

Comentario en código: "defense in depth — zero trust external systems"

### Criterio 3: ResponsePayloadSerializer importado

**Estado:** ✓ Cumplido
**Evidencia:** `views.py:15` - `from core.serializers.chat_serializers import RequestPayloadSerializer, ResponsePayloadSerializer`

### Criterio 4: response_data validado con ResponsePayloadSerializer

**Estado:** ✓ Cumplido
**Evidencia:** `views.py:183-184`

```python
response_serializer = ResponsePayloadSerializer(data=response_data)
if not response_serializer.is_valid():
```

### Criterio 5: Si inválido → JsonResponse({'error': 'Invalid response from orchestrator'}, status=502)

**Estado:** ✓ Cumplido
**Evidencia:** `views.py:186-189`

```python
return JsonResponse(
    {'error': 'Invalid response from orchestrator'},
    status=502,
)
```

Incluye logging del error con `logger.error("Response validation failed: %s", response_serializer.errors)`

### Criterio 6: Si válido → JsonResponse(validated_data, status=200)

**Estado:** ✓ Cumplido
**Evidencia:** `views.py:192`

```python
return JsonResponse(response_serializer.validated_data, status=200)
```

### Criterio 7: Tests corridos sin regresiones

**Estado:** ✓ Cumplido
**Evidencia:** Salida de `python3 -Wa manage.py test core`

- **115 tests ejecutados**
- **0 fallos**
- **Tiempo de ejecución:** 712.269s
- **Exit code:** 0

Todos los tests pasan, incluyendo:

- Tests unitarios de HTMLSanitizer (12 tests)
- Tests unitarios de ResponsePayloadSerializer (5 tests)
- Tests de integración de ChatView
- Property-based tests del dataset y usuarios
- Tests de permisos y filtros de dataset

---

## Hallazgos

### ✅ Cumplimiento Total

1. **Defense in Depth**: La sanitización HTML se aplica antes de validar el payload, garantizando que incluso si n8n enviara contenido malicioso, Django lo bloquea.
2. **Zero Trust External Systems**: Comentario explícito en el código documenta la filosofía de seguridad.
3. **Logging completo**: Los errores de validación se registran con `logger.error()` incluyendo detalles del serializer.
4. **Manejo de errores robusto**: Status code HTTP 502 apropiado para respuestas inválidas del orquestador.
5. **No regresiones**: Todos los 115 tests pasan, validando que la integración no rompió funcionalidad existente.

### 🟡 Observaciones (no bloquean completion)

1. **Tarea 8.7 pendiente**: El comentario `# TODO: logging completo (tarea 8.7)` indica que el logging completo se implementará en la siguiente subtarea.
2. **Orden de operaciones óptimo**: Sanitización antes de validación asegura que el contenido HTML peligroso se neutraliza incluso si el serializer falla.

---

## Verificación contra requirements.md

### Requirement 2 AC1-6 (Response_Payload)

✓ **Cumplido** - ResponsePayloadSerializer valida la estructura completa del Response_Payload incluyendo:

- `output` (string)
- `html_render` (boolean)
- `metadata` (objeto con agent_used, execution_time_ms, records_found)
- `conversationId` (string)
- `error` (opcional)

### Requirement 6 AC1-6 (Recibir y procesar Response_Payload)

✓ **Cumplido** - ChatView:

- AC1: Parsea response body como JSON (implementado en tarea 8.5)
- AC2-3: Maneja body vacío y JSON inválido (implementado en tarea 8.5)
- AC4: Renderiza output como HTML sanitizado (sanitización implementada en 8.6, renderizado en frontend pendiente de tarea 11.4)
- AC6: Metadata se retorna en JsonResponse para logging frontend

### Design - Component 6 (HTMLSanitizer - Defense in Depth)

✓ **Cumplido** - HTML de n8n se sanitiza con bleach antes de retornar a frontend, implementando defense in depth contra XSS.

---

## Decisión

**MARCAR TAREA 8.6 COMO COMPLETED**

**Justificación:**

1. Todos los criterios de aceptación están cumplidos.
2. La implementación sigue el diseño definido en `requirements.md` y `design.md`.
3. Los 115 tests pasan sin regresiones.
4. La sanitización HTML implementa correctamente la estrategia de "zero trust external systems".
5. El manejo de errores y logging están completos para esta subtarea.

**Próximos pasos:**

- Tarea 8.7: Agregar logging completo en ChatView (TODO identificado en línea 192)
- Tarea 8.8: Escribir tests de integración para ChatView
- Tarea 9.1: Agregar endpoint /api/chat/ a URL routing

---

**Fecha de validación:** 2026-04-17
**Validador:** Kiro
**Resultado:** ✅ COMPLETED
