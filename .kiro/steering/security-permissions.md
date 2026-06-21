---
inclusion: always
---

# Seguridad y permisos

## Dataset histórico
- El filtro de permisos se aplica antes de armar el contexto para el LLM, nunca después.
- Perfil Usuario no accede a registros con destinatario que contenga:
  - macro
  - macroestructura
  - líderes
  - lideres
- Debe priorizarse la comunicación más reciente cuando hay versiones viejas y nuevas;
  no mezclar sin aclaración explícita en la respuesta.
- Registros marcados sin_informacion no se tratan como contenido final ni válido.
- Links restringidos no se presentan como accesibles a perfiles sin permiso.

## Secretos
- Nunca hardcodear claves.
- Nunca leer ni mostrar el contenido de .env real (el que tiene valores completados).
- .env.example SÍ puede leerse y editarse: no tiene secretos, solo nombres de variables.
  Sirve para que Claude Code sepa qué variables existen sin exponer valores reales.
- Nunca commitear credenciales reales ni el archivo .env real.

## Ejecución automática
- No usar auto mode ni bypassPermissions como modo normal de este repo.
- plan es el modo por defecto; acceptEdits solo para refactors locales ya revisados.

## Trazabilidad obligatoria
- Toda ejecución de agente o workflow deja registro: usuario, fecha, mensaje, intención,
  agente seleccionado, permisos aplicados, resultado, errores.
- Sin trazabilidad, una tarea de implementación no se considera completa, aunque el
  código funcione.

## Datos saliendo del workspace hacia herramientas externas
- Si en algún punto del desarrollo se usa una herramienta externa al workspace (por
  ejemplo, pegar contenido en una conversación aparte con Claude para una segunda
  opinión de diseño, fuera de Kiro), solo puede salir: el brief, los archivos de
  spec (requirements/design/tasks), y el esquema de campos del dataset (nombres,
  no valores).
- Nunca debe salir del workspace: contenido real de mails/output/relevamiento_enriquecido.json,
  fragmentos reales de mails, ni datos de perfiles o usuarios reales — ni siquiera
  recortados o anonimizados a mano, porque la anonimización manual no es confiable.
- Si hace falta ejemplificar una estructura de datos para una herramienta externa,
  usar datos ficticios inventados a propósito para el ejemplo.
