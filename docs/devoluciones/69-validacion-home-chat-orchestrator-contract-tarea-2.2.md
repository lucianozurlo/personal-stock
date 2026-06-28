# Validación: home-chat-orchestrator-contract — Tarea 2.2

**Fecha:** 2026-06-26
**Spec:** home-chat-orchestrator-contract
**Tarea:** 2.2 — Implementar gestión de conversationId en sesión
**Archivo modificado:** `app/core/helpers/conversation.py`
**Validador:** Kiro

---

## Qué se implementó

Se agregaron dos classmethods a `ConversationIdManager`:

- `get_or_create(session)`: obtiene el `conversationId` de la sesión si existe; si no, genera uno nuevo, lo guarda en `session['conversationId']` y marca `session.modified = True`.
- `reset(session)`: genera siempre un nuevo `conversationId`, lo sobreescribe en `session['conversationId']` y marca `session.modified = True`.

---

## Verificación

**Comando ejecutado por Claude Code:**

```bash
DJANGO_SECRET_KEY=test-key DATABASE_URL=sqlite:///db.sqlite3 python3 -c "..."
```

**Salida:**

```
Generado: conv-th8vnb-d8upk4
Reutilizado: conv-th8vnb-d8upk4
Reset: conv-th8vnb-hc8t8e
Todos los criterios OK
```

---

## Análisis de Cumplimiento

### Requirement 4 (ConversationId en Django_Frontend)

**AC2**: ✅ `get_or_create` almacena conversationId en `request.session['conversationId']`
**AC3**: ✅ `get_or_create` reutiliza el ID existente de la sesión
**AC4**: ✅ `reset` genera nuevo ID y lo guarda en sesión
**AC5**: ✅ `get_or_create` genera ID cuando no existe en sesión

### Criterios de Tarea 2.2

1. ✅ Implementa `get_or_create(session)` que obtiene o crea ID
2. ✅ Implementa `reset(session)` que resetea ID
3. ✅ Usa `SESSION_KEY = 'conversationId'` para storage
4. ✅ Marca `session.modified = True` después de modificar

---

## Criterios de aceptación (Tabla de Claude Code)

| Criterio                                                                                                               | Estado | Evidencia                                                                                |
| ---------------------------------------------------------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------- |
| `get_or_create(session)` genera ID si no existe en sesión, guarda en `session[SESSION_KEY]`, `session.modified = True` | ✅ sí  | `session.get('conversationId') == id1` y `session.modified == True` verificados          |
| `get_or_create(session)` reutiliza ID existente sin tocar `session.modified`                                           | ✅ sí  | `id1 == id2` y `session.modified == False` verificados                                   |
| `reset(session)` genera nuevo ID, sobreescribe `session[SESSION_KEY]`, `session.modified = True`                       | ✅ sí  | `id3 != id1`, `session['conversationId'] == id3`, `session.modified == True` verificados |
| `SESSION_KEY = 'conversationId'` usada como clave de sesión                                                            | ✅ sí  | `ConversationIdManager.SESSION_KEY == 'conversationId'` verificado                       |

---

## Hallazgos

**Positivos:**

- Implementación completa según criterios de aceptación
- Lógica correcta para `get_or_create` (no marca `modified` si el ID ya existía)
- Lógica correcta para `reset` (siempre marca `modified`)
- Uso apropiado de classmethods
- Código limpio y legible
- Claude Code verificó comportamiento con script de prueba

**Sin problemas detectados.**

---

## Diff

`app/core/helpers/conversation.py` — se agregaron 14 líneas al final de la clase `ConversationIdManager`:

```python
@classmethod
def get_or_create(cls, session) -> str:
    conversation_id = session.get(cls.SESSION_KEY)
    if not conversation_id:
        conversation_id = cls.generate_conversation_id()
        session[cls.SESSION_KEY] = conversation_id
        session.modified = True
    return conversation_id

@classmethod
def reset(cls, session) -> str:
    conversation_id = cls.generate_conversation_id()
    session[cls.SESSION_KEY] = conversation_id
    session.modified = True
    return conversation_id
```

Sin otros archivos modificados.

---

## Veredicto

**✅ COMPLETED**

La tarea 2.2 cumple todos los criterios de aceptación de:

- Requirement 4 AC2-5 (requirements.md)
- Tarea 2.2 (tasks.md)

**Acciones tomadas:**

1. ✅ Tarea 2.2 marcada como `[x]` en tasks.md
2. ✅ PROGRESO.md actualizado:
   - Spec actual: home-chat-orchestrator-contract
   - Tarea actual: 2.3
   - Último gate pasado: tarea 2.2 completed — validación Kiro OK
   - Next: Paso 3.4 — implementar tarea 2.3 con Claude Code
3. ✅ Historial de validaciones actualizado con entrada para tarea 2.2

**Siguiente tarea:** 2.3 — Escribir tests unitarios para ConversationIdManager
