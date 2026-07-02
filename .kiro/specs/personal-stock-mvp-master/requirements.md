# Spec Maestro: Personal Stock MVP

## Introducción

Este documento es el spec maestro que coordina los 9 specs separados del Personal Stock MVP.
Define la lista completa de specs, sus tipos (Standard Feature / Quick Plan), la tabla de
dependencias entre ellos, el orden de implementación, y el estado actual de cada spec.

**NO se implementa directamente**: sirve como mapa de ruta y registro de progreso.

**Fecha de creación**: 2026-06-21
**Última actualización**: 2026-07-01 (spec 4 acciones-trazabilidad-metricas → completed)

---

## Glosario

- **Standard Feature Spec**: Spec que sigue el workflow completo (requirements con formato EARS → design técnico detallado → tasks con subtareas). Obligatorio para specs con lógica de negocio, permisos o contratos entre sistemas.
- **Quick Plan**: Spec simplificado que genera requirements, design y tasks automáticamente sin revisión paso a paso. Aceptable para specs estructurales o de documentación.
- **Estado completed**: El código del spec está funcionando y validado, no solo aprobado en papel.
- **Dependencia de implementación**: Un spec B depende de A si las TAREAS de B no pueden ejecutarse hasta que las tareas de A estén completed (código funcionando).

---

## Lista de Specs

| #   | Spec                              | Tipo                                  | Estado      |
| --- | --------------------------------- | ------------------------------------- | ----------- |
| 1   | base-django-login-home            | Standard Feature (Requirements-first) | completed   |
| 2   | usuarios-demo-perfiles-permisos   | Standard Feature (Requirements-first) | completed   |
| 3   | home-chat-orchestrator-contract   | Standard Feature (Requirements-first) | completed   |
| 4   | acciones-trazabilidad-metricas    | Standard Feature (Requirements-first) | completed   |
| 5   | rag-mails-dataset-permissions     | Standard Feature (Requirements-first) | sin empezar |
| 6   | trigger-comunicaciones-email      | Standard Feature (Requirements-first) | sin empezar |
| 7   | contenido-heredado-y-navegacion   | Quick Plan                            | sin empezar |
| 8   | memoria-feedback-correcciones     | Standard Feature (Requirements-first) | sin empezar |
| 9   | documentacion-local-y-limites-mvp | Quick Plan                            | sin empezar |

---

## Tabla de Dependencias

| Spec                              | Depende de                       | Por qué                                                                                                                                   |
| --------------------------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| base-django-login-home            | —                                | Es la base; nada se construye antes.                                                                                                      |
| usuarios-demo-perfiles-permisos   | base-django-login-home           | Necesita sesión y login funcionando para asociar perfil al usuario logueado.                                                              |
| home-chat-orchestrator-contract   | usuarios-demo-perfiles-permisos  | El contrato de entrada lleva `profile`, `roles` y `memory_enabled` del usuario.                                                           |
| acciones-trazabilidad-metricas    | home-chat-orchestrator-contract  | No hay qué trazar sin que exista una ejecución de orquestador.                                                                            |
| rag-mails-dataset-permissions     | usuarios-demo-perfiles-permisos  | El filtro de permisos necesita el modelo de perfil/rol ya definido.                                                                       |
| rag-mails-dataset-permissions     | home-chat-orchestrator-contract  | Se invoca como agente desde el orquestador, necesita el contrato de entrada/salida.                                                       |
| rag-mails-dataset-permissions     | acciones-trazabilidad-metricas   | security-permissions.md exige trazabilidad obligatoria de toda ejecución de agente; la consulta RAG es una ejecución de agente.           |
| trigger-comunicaciones-email      | home-chat-orchestrador-contract  | Se dispara como agente desde el orquestador.                                                                                              |
| trigger-comunicaciones-email      | acciones-trazabilidad-metricas   | Cada proyecto de comunicación debe quedar trazado.                                                                                        |
| contenido-heredado-y-navegacion   | base-django-login-home           | Depende de que exista layout y menú lateral del home. (Decisión tomada: el contenido heredado NO se filtra por perfil.)                   |
| memoria-feedback-correcciones     | usuarios-demo-perfiles-permisos  | El toggle de memoria es por usuario.                                                                                                      |
| memoria-feedback-correcciones     | acciones-trazabilidad-metricas   | Feedback y correcciones del usuario sobre respuestas del agente deben quedar trazados (mismo criterio que rag-mails-dataset-permissions). |
| documentacion-local-y-limites-mvp | todos los anteriores (specs 1-8) | Es el cierre; documenta lo ya implementado.                                                                                               |

---

## Regla de Paralelismo

Derivada de la tabla de dependencias:

- **rag-mails-dataset-permissions** y **trigger-comunicaciones-email** pueden desarrollarse en paralelo entre sí (no dependen una de la otra), pero ninguna de las dos puede empezar antes de que **home-chat-orchestrator-contract** Y **acciones-trazabilidad-metricas** estén en estado `completed`.
- **No correr "Run all Tasks"** sobre specs que todavía no tienen su dependencia directa en estado `completed`. Verificar este estado antes de lanzar ejecución paralela.
- Preferir serialización sobre paralelismo si hay riesgo de rate limiting (429) o drift de datos.

---

## Secuencia de Implementación Recomendada

```
1. base-django-login-home
2. usuarios-demo-perfiles-permisos
3. home-chat-orchestrator-contract
4. acciones-trazabilidad-metricas
5a. rag-mails-dataset-permissions    ─┐ paralelo posible
5b. trigger-comunicaciones-email     ─┘ (no dependen entre sí)
6. contenido-heredado-y-navegacion
7. memoria-feedback-correcciones
8. documentacion-local-y-limites-mvp
```

Esta secuencia respeta todas las dependencias y maximiza eficiencia sin riesgo de bloqueos.

---

## Decisiones Consolidadas

Las siguientes decisiones ya fueron tomadas durante el inventario-diagnóstico y están incorporadas en los specs correspondientes. **NO son riesgos abiertos**:

### Decisión 1: Home → home.html (renombrado)

- **Contexto**: El archivo fuente se llama `templates/index.html`, pero el brief lo menciona como `home.html`.
- **Decisión tomada**: renombrar `templates/index.html` → `templates/home.html` en la primera tarea del spec 1.
- **Impacto**: Todas las referencias en steering files, specs y código apuntan a `home.html`.
- **Documentado en**: spec `base-django-login-home` (tarea explícita de renombrado).

### Decisión 2: Assets de templates

- **Contexto**: Los assets de templates están distribuidos en subdirectorios.
- **Decisión tomada**:
  - Estilos: `templates/css/`
  - Scripts: `templates/js/`
  - Logos: `templates/img/`
- **Impacto**: Configuración de `STATICFILES_DIRS` en Django debe incluir estas rutas.
- **Documentado en**: spec `base-django-login-home` (configuración de settings.py).

### Decisión 3: Dataset indexado, no carga completa

- **Contexto**: `relevamiento_enriquecido.json` tiene ~5.300 registros (~169k líneas). Cargar todo en memoria por consulta es lento.
- **Decisión tomada**: crear índice compacto JSONL o usar SQLite FTS5, cargar en memoria al inicio (caching simple).
- **Impacto**: El spec 5 debe incluir tarea de indexación/caching, no lectura directa del JSON completo.
- **Documentado en**: spec `rag-mails-dataset-permissions` (tarea de indexación).

### Decisión 4: Reemplazo de "Benja" hardcodeado

- **Contexto**: "Benja" aparece hardcodeado en múltiples lugares:
  - `templates/home.html`: `<span id="welcomeTitle">Hola, Benja.</span>`
  - `templates/js/app.js`: array `RANDOM_GREETINGS` con "Hola Benja!"
- **Decisión tomada**: reemplazar solo en `templates/` y `./app/` (NO tocar `cs-chat-rag/`):
  - En `home.html`: usar template tag Django `{{ user.first_name }}`.
  - En `app.js`: obtener `userId` desde sesión Django (endpoint `/api/me/` o contexto embebido).
- **Impacto**: Spec 1 debe incluir tarea explícita de reemplazo.
- **Documentado en**: spec `base-django-login-home` (tarea de parametrización de usuario).

### Decisión 5: DATABASE_URL cableada con dj-database-url

- **Contexto**: `.env.example` declara `DATABASE_URL` pero la dependencia `dj-database-url` no está instalada.
- **Decisión tomada**: la primera tarea del spec 1 (bootstrap Django) debe:
  1. Instalar `dj-database-url` en `requirements.txt`
  2. Cablearla en `settings.py`: `DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])`
- **Impacto**: Ninguna tarea se considera completa si declara una variable de entorno sin cableo real en código (per tech.md).
- **Documentado en**: spec `base-django-login-home` (tarea de configuración de settings.py).

### Decisión 6: Contenido heredado de Comustock — acceso amplio

- **Contexto**: La sección 7 del inventario-diagnóstico preguntaba si el contenido heredado se filtra por perfil.
- **Decisión tomada**: el contenido heredado de Comustock (logos, manuales, templates, etc.) es de acceso amplio para todo usuario autenticado. NO se filtra por perfil.
- **Impacto**:
  - El spec 7 (`contenido-heredado-y-navegacion`) es **Quick Plan** (no Standard Feature).
  - Solo depende de `base-django-login-home` (no de `usuarios-demo-perfiles-permisos`).
- **Documentado en**: este spec maestro (tabla de dependencias) y en spec 7.

---

## Riesgos Identificados (abiertos, no resueltos)

Estos riesgos requieren mitigación durante la implementación de los specs correspondientes:

### Riesgo 1: Compatibilidad cs-chat-rag ↔ Django

- **Severidad**: ALTA
- **Descripción**: `cs-chat-rag/` es un proyecto independiente (n8n + postgres + nginx + vanilla JS), NO una base Django reutilizable. No se puede "convertir" sin reescribir toda la lógica.
- **Mitigación**:
  1. Crear `./app` Django desde cero.
  2. Reutilizar SOLO: schema PostgreSQL de memoria conversacional, patrón de orquestación n8n, inspiración UI.
  3. NO importar `cs-chat-rag` como módulo Python (no es código Python).
  4. Documentar explícitamente qué se hereda y qué se reescribe.
- **Documentado en**: specs 1, 3 y 8.

### Riesgo 2: n8n no disponible localmente

- **Severidad**: MEDIA
- **Descripción**: Si n8n no corre en `localhost:5678`, el orquestador no funciona y todas las intenciones del usuario quedan bloqueadas.
- **Mitigación** (per tech.md):
  1. Crear función/vista Django mock que reciba el mismo payload del webhook n8n.
  2. Responder con JSON coherente con el contrato de salida del brief (sección 8).
  3. Marcar trazabilidad como `simulado: true`.
  4. Dejar `TODO` explícito en código.
- **Documentado en**: spec `home-chat-orchestrator-contract` (tarea de fallback mock).

### Riesgo 3: Campos del dataset que el brief asume pero no existen

- **Severidad**: BAJA
- **Descripción**: Los primeros registros de `relevamiento_enriquecido.json` confirman que todos los campos documentados en `ESTRUCTURA_DATASET.md` están presentes, pero puede aparecer algún campo faltante durante implementación.
- **Mitigación** (per rules.md): ante conflicto entre brief y estructura real, **frenar y preguntar**. Señalar discrepancia exacta, proponer 1-2 alternativas, documentar decisión en spec.
- **Documentado en**: spec `rag-mails-dataset-permissions`.

---

## Alcance Detallado por Spec

### Spec 1 — base-django-login-home

- Crear proyecto Django en `./app/`
- Instalar y cablear `dj-database-url` con `DATABASE_URL` de `.env.example`
- Configurar `TEMPLATES[0]['DIRS']` → `BASE_DIR.parent / 'templates'`
- Configurar `STATICFILES_DIRS` para `templates/css/`, `templates/js/`, `templates/img/`
- Renombrar `templates/index.html` → `templates/home.html`
- Integrar `templates/login.html` en ruta `/login/`
- Integrar `templates/home.html` en ruta `/` (home)
- Sistema de autenticación básico (Django contrib.auth)
- **Reemplazar "Benja" hardcodeado** en `home.html` y `app.js` por usuario de sesión Django
- Sesión persistente (login funcional)

### Spec 2 — usuarios-demo-perfiles-permisos

- Modelo Usuario extendiendo AbstractUser
- Modelo Perfil: Administrador, Usuario IC, Heavy user, Macro, Usuario
- Modelo Rol: Diseñador, Desarrollador, Redactor, Productor, Gerente Cultura, Gerente IC, Especialista
- Fixtures con 100 usuarios demo (incluyendo los 12 usuarios de prueba del brief)
- Lógica de permisos: perfil "Usuario" NO accede a destinatarios con macro/macroestructura/líderes/lideres
- Toggle de memoria habilitada por usuario

### Spec 3 — home-chat-orchestrator-contract

- Definir contrato de entrada/salida común para todos los agentes (brief sección 8)
- Endpoint POST `/api/chat/` que recibe mensaje del usuario y llama a n8n
- Fallback mock si `N8N_WEBHOOK_URL` no responde (per tech.md)
- Clasificación de intención básica (las 11 categorías del brief sección 7)
- Respuesta con LLM base (Gemini) si no hay agente aplicable
- Integrar con `templates/js/app.js`: reemplazar `N8N_WEBHOOK_URL` por `/api/chat/`

### Spec 4 — acciones-trazabilidad-metricas

- Modelo WorkflowRun (trazabilidad de ejecuciones de agente/workflow)
- Modelo MetricEvent (métricas básicas)
- Endpoint `/api/actions/` para listar acciones del usuario actual
- Endpoint `/api/metrics/` (solo Administrador y Usuario IC)
- Página de acciones (template básico con listado)
- Registro automático de trazabilidad en cada llamada a `/api/chat/`

### Spec 5 — rag-mails-dataset-permissions

- Cargar/indexar `mails/output/relevamiento_enriquecido.json` (índice JSONL compacto o SQLite FTS5)
- Filtro de permisos ANTES de armar contexto: bloquear destinatarios restringidos para perfil "Usuario"
- Endpoint/workflow n8n que responde con contexto relevante + respuesta generada
- Integración con orquestador (intención: consulta_historial_mails)
- Reglas de vigencia (0-6 meses vigente, 6-18 aclarar, 18+ desactualizada)
- Trazabilidad obligatoria

### Spec 6 — trigger-comunicaciones-email

- Modelo Proyecto (id, solicitante, brief, audiencia, canal, estado, Focus, aprobadores, etc.)
- Workflow n8n con los 26 pasos del brief sección 22 (MVP 1: solo e-mail)
- Integración con orquestador (intención: generar_plan_comunicacion)
- Brief optimization + preguntas para completar datos faltantes
- Trazabilidad obligatoria

### Spec 7 — contenido-heredado-y-navegacion

- Servir contenido de `comustock-base/` como archivos estáticos
- Rutas Django para Stock, Templates, Mi firma, Toolbox, Roadmap
- Menú lateral funcional (colapsable, un solo menú activo a la vez)
- Carousel de atajos con los 8 accesos del brief sección 13
- Placeholders/estados vacíos para secciones no implementadas en MVP 1

### Spec 8 — memoria-feedback-correcciones

- Modelo UserMemory (memoria conversacional por usuario)
- Toggle de memoria en perfil de usuario
- Modelo AgentFeedback (feedback del usuario sobre respuestas del agente)
- Modelo CorrectionRecord (correcciones aplicadas por el usuario)
- Endpoint para enviar feedback/corrección
- Trazabilidad de feedback y correcciones

### Spec 9 — documentacion-local-y-limites-mvp

- README.md con instalación local paso a paso
- Documentación de límites MVP 1
- Qué está simulado/mockeado
- Dependencias externas (n8n, Gemini API, etc.)
- Documentación de estructura de carpetas
- Límites de escala (por qué no sirve para 20k usuarios sin cambios)

---

## Formato de Estado

El estado de cada spec puede ser:

- **sin empezar**: No se ha generado requirements.md
- **requirements**: requirements.md generado y aprobado
- **design**: design.md generado y aprobado
- **tasks**: tasks.md generado y aprobado
- **en implementación**: tareas en ejecución (al menos una tarea en progreso)
- **completed**: todas las tareas completadas y código validado

**Actualización de estado**: Kiro debe actualizar la tabla "Lista de Specs" al cierre de cada fase (requirements/design/tasks aprobado) y al completar cada tarea.

---

## Notas de Uso

- Este spec maestro NO se ejecuta directamente — no tiene tasks.md.
- Sirve como coordinador: antes de empezar un spec hijo, verificar en la tabla de dependencias que todos sus specs base estén en estado `completed`.
- Si un spec hijo falla validación o cambia de alcance, actualizar este spec maestro para reflejar el cambio (ej: nuevo riesgo, decisión resuelta, cambio de dependencia).
- Para retomar el trabajo después de un corte, consultar la columna "Estado" en la tabla "Lista de Specs" para saber dónde quedaste.

---

_Fin del spec maestro. Para iniciar specs hijos, seguir el orden de la secuencia recomendada._
