# Spec maestro: personal-stock-mvp-master

Este archivo es una PLANTILLA. Kiro debe generar su propia versión completa a partir
del prompt del Paso 2 ("Spec maestro con dependencias") en RUNBOOK.md. Usá esta
plantilla para revisar que lo que entregue Kiro tenga, como mínimo, esta forma.

Nota sobre "depende de" en la tabla: significa que las TAREAS de implementación del
spec dependiente no pueden ejecutarse hasta que las tareas del spec base estén
completed (código funcionando), no solo que el spec base esté aprobado en papel.
Un spec puede tener requirements+design+tasks aprobados y aun así no estar
implementado — la dependencia real se resuelve recién cuando el código existe.

## Lista de specs y orden sugerido

1. base-django-login-home
2. usuarios-demo-perfiles-permisos
3. home-chat-orchestrator-contract (fusiona contrato conversacional + contrato n8n)
4. acciones-trazabilidad-metricas
5. rag-mails-dataset-permissions
6. trigger-comunicaciones-email
7. contenido-heredado-y-navegacion
8. memoria-feedback-correcciones
9. documentacion-local-y-limites-mvp

## Tabla de dependencias (obligatoria, sin esto no se aprueba el spec maestro)

| Spec | Depende de | Por qué |
|---|---|---|
| base-django-login-home | — | Es la base; nada se construye antes. |
| usuarios-demo-perfiles-permisos | base-django-login-home | Necesita sesión y login funcionando para asociar perfil al usuario logueado. |
| home-chat-orchestrator-contract | usuarios-demo-perfiles-permisos | El contrato de entrada lleva profile, roles y memory_enabled del usuario. |
| acciones-trazabilidad-metricas | home-chat-orchestrator-contract | No hay qué trazar sin que exista una ejecución de orquestador. |
| rag-mails-dataset-permissions | usuarios-demo-perfiles-permisos | El filtro de permisos necesita el modelo de perfil/rol ya definido. |
| rag-mails-dataset-permissions | home-chat-orchestrator-contract | Se invoca como agente desde el orquestador, necesita el contrato de entrada/salida. |
| rag-mails-dataset-permissions | acciones-trazabilidad-metricas | security-permissions.md exige trazabilidad obligatoria de toda ejecución de agente; la consulta RAG es una ejecución de agente. |
| trigger-comunicaciones-email | home-chat-orchestrator-contract | Se dispara como agente desde el orquestador. |
| trigger-comunicaciones-email | acciones-trazabilidad-metricas | Cada proyecto de comunicación debe quedar trazado. |
| contenido-heredado-y-navegacion | base-django-login-home | Depende de que exista layout y menú lateral del home. |
| memoria-feedback-correcciones | usuarios-demo-perfiles-permisos | El toggle de memoria es por usuario. |
| memoria-feedback-correcciones | acciones-trazabilidad-metricas | Mismo criterio que rag-mails-dataset-permissions: una corrección o feedback del usuario sobre una respuesta del agente es una ejecución que debe quedar trazada. |
| documentacion-local-y-limites-mvp | todos los anteriores | Es el cierre; documenta lo ya implementado. |

**Nota — punto a confirmar, no a asumir:** la fila de `contenido-heredado-y-navegacion`
de arriba asume que ese spec es puramente de layout heredado (no filtra contenido
por perfil). Si al inspeccionar el brief real y `cs-chat-rag` aparece que el menú o
las secciones heredadas deben ocultarse o mostrarse según el perfil/rol del usuario,
esa fila pasa a depender también de `usuarios-demo-perfiles-permisos`. Kiro debe
confirmar esto explícitamente contra el brief antes de cerrar el spec maestro —
no se asume en ningún sentido de antemano (ver `rules.md`: ante ambigüedad, frenar
y preguntar).

## Regla de paralelismo derivada de esta tabla

- rag-mails-dataset-permissions y trigger-comunicaciones-email pueden desarrollarse
  en paralelo entre sí (no dependen una de la otra), pero ninguna de las dos puede
  empezar antes de que home-chat-orchestrator-contract Y acciones-trazabilidad-metricas
  estén cerrados — ambas dependen también de trazabilidad, no solo del contrato.
- No correr "Run all Tasks" sobre specs que todavía no tienen su dependencia directa
  en estado completed. Verificar este estado antes de lanzar ejecución paralela.

## Qué specs deben usar Standard Feature Spec vs Quick Plan

- Standard Feature Spec (obligatorio): usuarios-demo-perfiles-permisos,
  home-chat-orchestrator-contract, rag-mails-dataset-permissions,
  trigger-comunicaciones-email. Son specs con lógica de negocio, permisos o
  contratos entre sistemas — necesitan requirements con EARS y design completo.
- Quick Plan (aceptable si Kiro lo justifica): contenido-heredado-y-navegacion,
  documentacion-local-y-limites-mvp. Son mayormente estructurales o de documentación.

## Riesgos a pedirle a Kiro que liste explícitamente

- Qué pasa si cs-chat-rag ya tiene una estructura incompatible con ./app Django.
- Qué pasa si ESTRUCTURA_DATASET.md no incluye un campo que el brief asume que existe.
- Qué pasa si n8n no está disponible localmente durante el desarrollo (fallback).
- Qué pasa si el volumen real de mails en relevamiento_enriquecido.json es muy grande
  para cargarlo en memoria en cada consulta RAG del MVP local.

## Sugerencia opcional: columna de estado por spec

No es obligatorio para que el spec maestro se apruebe, pero con 9 specs y
sesiones separadas en el tiempo conviene que Kiro agregue una columna `Estado`
a la lista de specs (no a la tabla de dependencias) con valores tipo: `sin
empezar` / `requirements aprobado` / `design aprobado` / `tasks aprobado` /
`en implementación` / `completed`. Sirve para retomar el trabajo después de un
corte (o un 429) sin tener que releer cada spec para saber dónde quedaste.
Si lo pedís, que Kiro la mantenga actualizada al cierre de cada Paso 3 (gate
de 3.1–3.3) y de cada tarea cerrada en 3.5, no solo al crear el spec maestro.
