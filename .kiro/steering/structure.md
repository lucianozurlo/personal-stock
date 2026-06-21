---
inclusion: always
---

# Estructura del proyecto

## Workspace root
El workspace root es ~/Desktop/PS-edit.

## Política de carpetas
- El código de la app vive en ./app
- Los templates fuente entregados viven en ./templates (no se mueven ni se copian a ./app)
- El dataset y material heredado (mails, comustock-base, cs-chat-rag) permanecen fuera de
  ./app y se consumen por configuración o importación controlada, nunca copiados a ciegas
- Las specs viven en ./.kiro/specs
- El steering vive en ./.kiro/steering
- La configuración de Claude Code vive en ./.claude y ./CLAUDE.md

## Estructura objetivo
```
~/Desktop/PS-edit/
  .kiro/
    steering/
    specs/
  .claude/
    settings.json
  CLAUDE.md
  app/
    manage.py
    config/
    core/
    fixtures/
    tests/
  templates/
  mails/
  cs-chat-rag/
  comustock-base/
  comustock_base.csv
  ESTRUCTURA_DATASET.md
  brand_key_voz_tono_personal.md
  resumen proyecto previo (bot).md
```

## Regla de modificación
- No mover ni renombrar carpetas heredadas sin necesidad operacional validada y documentada.
- Si cs-chat-rag ya tiene una estructura de proyecto propia, ese inventario decide si ./app
  se crea desde cero o si se construye sobre esa base. No asumir, inspeccionar primero.
