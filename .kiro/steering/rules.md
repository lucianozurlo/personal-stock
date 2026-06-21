---
inclusion: always
---

# Reglas de proceso y resolución de conflictos

## Ante conflicto entre el brief y la estructura real de datos o código
Va a pasar: algo que el brief describe no calza exactamente con lo que hay en
ESTRUCTURA_DATASET.md, en relevamiento_enriquecido.json, o en cs-chat-rag.

Regla: frenar y preguntar. Nunca:
- inventar un campo, endpoint o estructura que no existe para que el brief "cierre"
- adaptar el brief en silencio a lo que es más fácil de implementar
- elegir la interpretación más conveniente sin dejarla documentada como decisión

Cuando aparezca un conflicto, Kiro debe:
1. Señalar exactamente qué dice el brief y qué muestra la fuente real.
2. Proponer 1-2 alternativas de resolución.
3. Esperar aprobación antes de reflejarlo en requirements.md o design.md.
4. Documentar la decisión final en el spec correspondiente, no solo en el chat.

## Disciplina de specs
- No se empieza a implementar sin spec plan, requirements y design aprobados.
- No se mezclan tareas de specs distintos en una sola sesión de Claude Code.
- Cada spec nuevo debe declarar de qué specs depende antes de poder ejecutarse
  (ver tabla de dependencias en personal-stock-mvp-master).
- Si una parte no puede completarse en MVP 1, queda marcada como simulada, mockeada
  o preparada para MVP posterior — nunca se omite en silencio.

## Disciplina de ejecución con Claude Code
- Una tarea por sesión. Si Claude Code propone avanzar a la siguiente tarea sin que
  la actual esté validada, se lo frena explícitamente.
- Si el criterio de aceptación no está claro, no se improvisa: se marca el gap y se
  vuelve a Kiro para resolverlo en el spec, no en el código.
- Después de que Claude Code reporta que una tarea cumple su criterio de aceptación,
  Kiro revalida ese resultado contra tasks.md y requirements.md antes de que la tarea
  se marque completed. La palabra de Claude Code sobre su propio trabajo no es
  suficiente para cerrar una tarea.

## Regla de paralelismo
- No ejecutar specs o tareas en paralelo si tienen dependencia de datos o de modelo
  entre sí (ver tabla de dependencias). Preferir serializar sobre arriesgar 429 o drift.
