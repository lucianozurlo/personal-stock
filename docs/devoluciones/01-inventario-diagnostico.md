# INVENTARIO Y DIAGNÓSTICO — Personal Stock MVP

> Documento generado por Kiro en base a inspección completa del workspace.
> Fecha: 2026-06-21
> Estado: pre-specs (ningún spec generado aún)

---

## 1. INVENTARIO DE INSUMOS

### 1.1 Estructura encontrada vs. brief

**Workspace root confirmado**: `/Users/luciano/Desktop/PS-edit`

**Carpetas confirmadas**:

- ✅ `.kiro/specs/` — contiene solo `personal-stock-mvp-master-TEMPLATE.md` (plantilla de referencia)
- ✅ `.kiro/steering/` — 5 archivos: product.md, rules.md, security-permissions.md, structure.md, tech.md
- ✅ `templates/` — con index.html (NO home.html), login.html, css/, js/, img/
- ✅ `cs-chat-rag/` — proyecto base existente (chatbot previo)
- ✅ `comustock-base/` — contenido heredado (HTML, CSS, assets)
- ✅ `mails/` — dataset histórico con relevamiento_enriquecido.json (~169k líneas, ~5.300 registros)
- ✅ `assets-personal-stock/` — referencias visuales y plan-de-agentes.csv
- ✅ `comustock_base.csv` — sitemap heredado (300+ líneas)
- ✅ `brand_key_voz_tono_personal.md` — manual de voz y tono
- ✅ `brief-personal-stock.md` — brief completo (1732 líneas)
- ✅ `CLAUDE.md` — instrucciones para Claude Code
- ✅ `PROGRESO.md` — vacío, listo para tracking
- ✅ `.env.example` — 4 variables declaradas

### 1.2 ¿Qué es cs-chat-rag?

**Tipo de proyecto**: chatbot previo con n8n + PostgreSQL + nginx + frontend vanilla JS
**NO es Django ni Flask** — es un proyecto independiente con:

| Componente             | Tecnología                                            |
| ---------------------- | ----------------------------------------------------- |
| Frontend               | HTML + CSS + JS (vanilla, sin frameworks pesados)     |
| Orquestación           | n8n (self-hosted)                                     |
| RAG                    | JSONL servido como estático vía nginx                 |
| Memoria conversacional | PostgreSQL 16                                         |
| LLM                    | Gemini 2.5 Flash + fallback Groq llama-3.3-70b        |
| Infraestructura local  | Docker Compose (postgres + nginx) + `npx n8n` en host |

**¿Tiene lógica de RAG?**: ✅ SÍ — workflow completo en
`n8n/workflow/Comustock_Etapa_2_4_Chat_RAG_DB_memory_FIX_estado.json`,
busca contexto en JSONL, mantiene memoria en PostgreSQL por `conversationId`.

**Estructura**:

```
cs-chat-rag/
├── prompt-comustock.html   # frontend del chat
├── css/styles.css
├── js/                     # config.js, api.js, composer.js, state.js, ui.js, main.js
├── rag/                    # JSONL de chunks del catálogo
├── n8n/
│   ├── workflow/           # workflow principal de n8n
│   ├── sql/                # init SQL de PostgreSQL
│   ├── examples/
│   └── docs/
├── docker-compose.yml
└── check_env.sh
```

**Conclusión**: cs-chat-rag NO es base Django reutilizable. La app Django de Personal Stock
(`./app`) se crea desde cero. Se puede reutilizar:

- Patrón de orquestación con n8n (estructura de workflows, contratos)
- Schema de memoria conversacional (PostgreSQL SQL init)
- Inspiración UI (composer, mensajes) — adaptar a templates Django, NO copiar JS directo

**No copiar archivos a ciegas** — integrar por configuración y referencia.

### 1.3 Templates visuales: discrepancias críticas

**❌ DISCREPANCIA 1 — Nombre de archivo HOME**

- Brief menciona: `templates/home.html`
- Realidad: el archivo se llama `templates/index.html`
- Steering (structure.md) no menciona explícitamente el nombre del archivo home
- **Impacto**: toda referencia a `home.html` en el brief debe interpretarse como `index.html`

**❌ DISCREPANCIA 2 — Usuario hardcodeado "Benja"**

- Brief dice: "js/config.js con `CHAT_USER_ID = 'benja'`"
- cs-chat-rag/js/config.js → SÍ tiene `const CHAT_USER_ID = "benja";`
- templates/js/app.js → TAMBIÉN tiene `RANDOM_GREETINGS = ["Hola Benja!", ...]` y lógica completa de chat
- **Impacto**: templates/ tiene su propio app.js con la misma lógica hardcodeada — ambos deben
  reemplazarse por usuario dinámico basado en sesión Django

**❌ DISCREPANCIA 3 — Saludo hardcodeado en index.html**

- index.html muestra: `<h1><span id="welcomeTitle">Hola, Benja.</span>`
- Brief espera: saludo personalizado basado en usuario logueado
- **Impacto**: el template ya viene con "Benja" hardcodeado en HTML — debe parametrizarse
  con template tag Django: `{{ user.first_name }}`

**✅ CONFIRMADO — Logos**

- Brief menciona: `templates/personal-stock-logo.svg` y `templates/personal-stock-logo-light.svg`
- Realidad: están en `templates/img/personal-stock-logo.svg` y `templates/img/personal-stock-logo-light.svg`
- **Ruta correcta**: `templates/img/` (subdirectorio, no raíz de templates/)

### 1.4 Dataset histórico de mails

**Fuente confirmada**: `mails/output/relevamiento_enriquecido.json`
**Volumen**: ~169.413 líneas — estimación ~5.300 registros (array JSON)

**Esquema de campos** (documentado en ESTRUCTURA_DATASET.md, confirmado en inspección):

| Grupo                   | Campos                                                                                                                                                                                                    |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Base de la comunicación | id_mail, fecha_envio, asunto, proyecto, destinatario, copy_completo, resumen, estilo_diseno, tono_mensaje, categoria_probable, observaciones                                                              |
| Booleanos de tipo       | entradas_evento, evento_detalle, es_fallecimiento, es_encuesta, es_sorteo, es_ganadores, sin_informacion                                                                                                  |
| Destinatarios CCO       | cuentas_cco (número), cuentas_cco_total (número), destinatarios_total (número)                                                                                                                            |
| Agrupación (segmentada) | mails_en_grupo (número), ids_del_grupo (texto)                                                                                                                                                            |
| Imágenes                | imagenes_descargadas (número), nombres_imagenes (texto), nombres_partes (texto)                                                                                                                           |
| Tandas                  | posible_tanda (booleano), grupo_tanda (texto)                                                                                                                                                             |
| Links                   | links_detectados (texto), cantidad_links (número), links_accesibles (número), links_restringidos (número), links_rotos (número), links_detalle (array), links_contenido_md (texto), links_resumen (texto) |
| Adjuntos                | tiene_adjuntos (booleano), nombres_adjuntos (texto), adjuntos_detalle (array), adjuntos_contenido_md (texto), adjuntos_resumen (texto)                                                                    |

**Archivos complementarios**:

- `mails/output/contenido_md/` — markdown de links accesibles y adjuntos extraídos
- `mails/images/` — imágenes de las comunicaciones (incluyendo `*_UNIDA.png`)
- `mails/attachments/` — adjuntos originales
- `mails/workflows-n8n/` — workflows de procesamiento del dataset

### 1.5 Contenido heredado Comustock

**Sitemap CSV**: `comustock_base.csv` — 300+ líneas, delimitador `;`
Columnas principales: `orden_base; tipo_registro; seccion; pagina; Marca; ruta_relativa; area_principal; nombre_recurso; formatos_disponibles; descripcion_clara; tiene_descargas`

**Contenido HTML** (`comustock-base/`):

- `brands/` — 8 marcas: fibra, flow, movil, pay, personal, smarthome, tech, tienda
- `sections/` — 13 secciones HTML: CARTELERAS, E-MAILS, FUENTES, HOJAS MEMBRETADAS, ICONOS, IMAGENES, MI-FIRMA, PRESENTACIONES, PUBLICIDADES, TOOLKIT DISENO, TOOLKIT REDACTAR, VIVA-ENGAGE
- `content/` — audiovisuales, identidad, recursos, templates
- `assets/` — css, fonts, img, js (incluyendo tipografía Pulso)

**Conclusión**: contenido heredado es extenso y estructurado — debe integrarse por configuración
(rutas estáticas servidas por Django) o migración selectiva, NO copiado a ciegas a `./app`.

### 1.6 Configuración y proceso

**CLAUDE.md** — define workflow de Claude Code:

- Lectura obligatoria de steering files vía `@.kiro/steering/...`
- Una tarea por sesión
- No marcar completed sin validación de Kiro
- Commits atómicos: `tipo(spec-id): descripción — tarea X.Y`

**.env.example** — 4 variables declaradas:

```
DATABASE_URL=sqlite:///db.sqlite3
GEMINI_API_KEY=
N8N_WEBHOOK_URL=http://localhost:5678/webhook/
SECRET_KEY=
```

**❌ DISCREPANCIA CRÍTICA — Dependencia explícita no cableada**:

- `tech.md` dice: "Ninguna tarea se considera completa si declara `DATABASE_URL`
  sin ese cableo real en código" (`dj-database-url` en `settings.py`)
- `.env.example` declara `DATABASE_URL` pero NO existe `./app` todavía
- **Acción requerida**: la primera tarea (bootstrap Django) debe instalar `dj-database-url`
  y cablearla en `settings.py`

---

## 2. RIESGOS IDENTIFICADOS

### 2.1 Compatibilidad cs-chat-rag ↔ Django

**Severidad**: ALTA

cs-chat-rag es un proyecto completo independiente (n8n + postgres + nginx + vanilla JS),
NO una base Django reutilizable. No se puede "convertir" sin reescribir toda la lógica.

**Mitigación**:

1. Crear `./app` Django desde cero
2. Reutilizar SOLO: schema PostgreSQL de memoria conversacional, patrón de orquestación n8n, inspiración UI
3. NO importar cs-chat-rag como módulo Python (no es código Python)
4. Documentar explícitamente qué se hereda y qué se reescribe

### 2.2 Templates con usuario hardcodeado "Benja"

**Severidad**: MEDIA

templates/index.html y templates/js/app.js tienen "Benja" hardcodeado en múltiples lugares.
Si se integran sin modificar, el MVP mostrará "Benja" a todos los usuarios.

**Mitigación**:

1. Parametrizar saludo en index.html con template tag Django: `{{ user.first_name }}`
2. Reescribir app.js para obtener userId desde sesión Django (endpoint `/api/me/` o contexto embebido)
3. Eliminar `RANDOM_GREETINGS` con "Benja" hardcodeado — generar dinámicamente
4. Añadir tarea explícita en spec `base-django-login-home` para reemplazar hardcoded "Benja"

### 2.3 Volumen del dataset histórico

**Severidad**: MEDIA-ALTA

relevamiento_enriquecido.json tiene ~169k líneas (~5.300 registros). Cargar todo en memoria
en cada consulta RAG puede ser lento para MVP local. Sin indexación, la búsqueda es O(n).

**Mitigación**:

1. NO cargar el JSON completo por consulta
2. Crear índice JSONL compacto con campos clave: id_mail, resumen, copy_completo, destinatario, fecha_envio
3. Para MVP 1: cargar índice en memoria al inicio (caching simple) o usar SQLite FTS5
4. Documentar en spec `documentacion-local-y-limites-mvp` que para 20k usuarios
   se necesita vector DB (Pinecone, Weaviate, etc.)

### 2.4 n8n no disponible localmente

**Severidad**: MEDIA

Si n8n no corre, el orquestador no funciona y todas las intenciones del usuario quedan bloqueadas.

**Mitigación** (per tech.md):

1. Crear función/vista Django mock que reciba el mismo payload del webhook n8n
2. Responder con JSON coherente con el contrato de salida del brief (sección 8)
3. Marcar trazabilidad como `simulado: true`
4. Dejar `TODO` explícito en código
5. Añadir tarea en spec `home-chat-orchestrator-contract` para implementar fallback mock

### 2.5 Discrepancias brief ↔ realidad

**Severidad**: BAJA

El brief y el steering pueden diferir (ej: home.html vs. index.html, rutas de logos).

**Mitigación** (per rules.md):

- Ante conflicto entre brief y estructura real, **frenar y preguntar**
- Señalar discrepancia exacta, proponer 1-2 alternativas, documentar decisión en spec

### 2.6 Campos del dataset que el brief asume pero no existen

**Severidad**: BAJA

Los primeros registros de relevamiento_enriquecido.json confirman que todos los campos
documentados en ESTRUCTURA_DATASET.md están presentes. Riesgo bajo, pero si durante
implementación aparece un campo faltante, aplicar regla de rules.md.

---

## 3. DISCREPANCIAS ENTRE STEERING Y LO INSPECCIONADO

### 3.1 structure.md vs. realidad

**Estructura objetivo en structure.md**:

```
~/Desktop/PS-edit/
  .kiro/steering/
  .kiro/specs/
  .claude/settings.json
  CLAUDE.md
  app/ (manage.py, config/, core/, fixtures/, tests/)
  templates/
  mails/
  cs-chat-rag/
  comustock-base/
  comustock_base.csv
  ...
```

**Discrepancias**:

- ❌ `./app/` NO existe aún (se creará en primera tarea — esperado)
- ✅ Archivos adicionales no mencionados en structure.md pero no conflictivos:
  `brief-personal-stock.md`, `PROGRESO.md`, `.env.example`, `assets-personal-stock/`

**Conclusión**: structure.md es preciso para las carpetas clave.

### 3.2 tech.md vs. realidad

**tech.md dice**: "Mantener templates fuente en ./templates (NO dentro de ./app) y conectarlos
por configuración de Django: agregar a `TEMPLATES[0]['DIRS']` en `settings.py` usando
`BASE_DIR.parent / 'templates'`"
**Realidad**: ✅ templates/ existe en raíz del workspace — coincide.

**tech.md dice**: "No dejar variables de entorno declaradas en .env.example sin uso real
cableado en el código"
**Realidad**: ❌ `.env.example` declara `DATABASE_URL` pero `./app` no existe aún.
Acción requerida en primera tarea.

**Conclusión**: tech.md es preciso — la primera tarea debe cumplir todas las reglas de cableo.

### 3.3 product.md vs. realidad

**product.md dice**: "templates/home.html es la fuente principal de home."
**Realidad**: ❌ `home.html` NO existe — el archivo se llama `templates/index.html`.
**Acción requerida**: todas las referencias a "home.html" en product.md deben
interpretarse como "index.html". Corregir product.md en primera tarea o al generar el spec
`base-django-login-home` (decisión a documentar en el spec).

**product.md dice**: "templates/personal-stock-logo.svg y templates/personal-stock-logo-light.svg"
**Realidad**: ❌ los logos están en `templates/img/` (subdirectorio), no en raíz de templates/.
Rutas correctas:

- `templates/img/personal-stock-logo.svg`
- `templates/img/personal-stock-logo-light.svg`

### 3.4 Chequeo puntual obligatorio: CHAT_USER_ID = "benja"

**Brief dice**: "En el chatbot base existe js/config.js con `CHAT_USER_ID = 'benja'`"

**Realidad encontrada**:

| Archivo                    | CHAT_USER_ID                      | "Benja" hardcodeado                                     |
| -------------------------- | --------------------------------- | ------------------------------------------------------- |
| `cs-chat-rag/js/config.js` | ✅ `const CHAT_USER_ID = "benja"` | ✅ en RANDOM_GREETINGS                                  |
| `templates/js/app.js`      | ❌ NO tiene CHAT_USER_ID          | ✅ en RANDOM_GREETINGS y `"Hola, Benja."` en index.html |

**Discrepancia**: el brief asume que solo hay un `config.js`, pero hay DOS archivos JS con
lógica de chat:

1. `cs-chat-rag/js/config.js` — proyecto previo, **NO se usa en Django**
2. `templates/js/app.js` — template para Django, **SE usará — DEBE modificarse**

`templates/js/app.js` NO tiene `CHAT_USER_ID` explícito, pero sí tiene "Benja" hardcodeado
en RANDOM_GREETINGS y la lógica completa de chat. Es el archivo que debe
modificarse para usar usuario dinámico.

---

## 4. STEERING FALTANTE

### 4.1 Archivos steering presentes

✅ Todos los steering files mencionados en CLAUDE.md están presentes y cargados:

- `product.md`
- `tech.md`
- `structure.md`
- `security-permissions.md`
- `rules.md`

### 4.2 Steering recomendado pero no crítico para arrancar

**Sugerencia 1: `testing.md`**
Actualmente tech.md menciona "Implementar pruebas mínimas por spec" pero no detalla:

- Framework de testing recomendado (pytest-django, unittest)
- Cobertura mínima requerida por tipo de spec
- Tipos de tests obligatorios por capa (models, views, integración, RAG, permisos)

**Sugerencia 2: `mvp-limits.md`**
product.md dice "El MVP 1 correrá localmente" pero no detalla:

- Qué cambios se necesitan para escalar a 20k usuarios (vector DB, caching, CDN)
- Límites de concurrencia esperados en MVP local
- Infraestructura mínima recomendada (RAM, disco para el dataset)

**Conclusión**: los steering presentes son suficientes para arrancar. Los dos sugeridos
pueden generarse al crear el spec `documentacion-local-y-limites-mvp`.

---

## 5. PROPUESTA DE SPECS SEPARADOS

| #   | Spec                              | Tipo                                  | Estado      |
| --- | --------------------------------- | ------------------------------------- | ----------- |
| 1   | base-django-login-home            | Standard Feature (Requirements-first) | sin empezar |
| 2   | usuarios-demo-perfiles-permisos   | Standard Feature (Requirements-first) | sin empezar |
| 3   | home-chat-orchestrator-contract   | Standard Feature (Requirements-first) | sin empezar |
| 4   | acciones-trazabilidad-metricas    | Standard Feature (Requirements-first) | sin empezar |
| 5   | rag-mails-dataset-permissions     | Standard Feature (Requirements-first) | sin empezar |
| 6   | trigger-comunicaciones-email      | Standard Feature (Requirements-first) | sin empezar |
| 7   | contenido-heredado-y-navegacion   | Quick Plan (ver nota\*)               | sin empezar |
| 8   | memoria-feedback-correcciones     | Standard Feature (Requirements-first) | sin empezar |
| 9   | documentacion-local-y-limites-mvp | Quick Plan                            | sin empezar |

**Nota\***: si el contenido heredado se filtra por perfil/rol del usuario, contenido-heredado-y-navegacion
pasa a ser Standard Feature Spec. **Pregunta pendiente al usuario**: ¿El contenido heredado de
Comustock (logos, manuales, templates) se filtra por perfil o es accesible para todos los usuarios?

---

### Detalle de alcance por spec

#### spec 1 — base-django-login-home

- Crear proyecto Django en `./app/`
- Instalar y cablear `dj-database-url` con `DATABASE_URL` de `.env.example`
- Configurar `TEMPLATES[0]['DIRS']` → `BASE_DIR.parent / 'templates'`
- Configurar `STATICFILES_DIRS` para `templates/img/` (logos)
- Integrar `templates/login.html` en ruta `/login/`
- Integrar `templates/index.html` en ruta `/` (home) — NO home.html
- Sistema de autenticación básico (Django contrib.auth)
- **Reemplazar "Benja" hardcodeado** en index.html y app.js por usuario de sesión Django
- Sesión persistente (login funcional)

#### spec 2 — usuarios-demo-perfiles-permisos

- Modelo Usuario extendiendo AbstractUser
- Modelo Perfil: Administrador, Usuario IC, Heavy user, Macro, Usuario
- Modelo Rol: Diseñador, Desarrollador, Redactor, Productor, Gerente Cultura, Gerente IC, Especialista
- Fixtures con 100 usuarios demo (incluyendo los 12 usuarios de prueba del brief)
- Lógica de permisos: perfil "Usuario" NO accede a destinatarios con macro/macroestructura/líderes/lideres
- Toggle de memoria habilitada por usuario

#### spec 3 — home-chat-orchestrator-contract

- Definir contrato de entrada/salida común para todos los agentes (brief sección 8)
- Endpoint POST `/api/chat/` que recibe mensaje del usuario y llama a n8n
- Fallback mock si `N8N_WEBHOOK_URL` no responde (per tech.md)
- Clasificación de intención básica (las 11 categorías del brief sección 7)
- Respuesta con LLM base (Gemini) si no hay agente aplicable
- Integrar con templates/js/app.js: reemplazar `N8N_WEBHOOK_URL` por `/api/chat/`

#### spec 4 — acciones-trazabilidad-metricas

- Modelo WorkflowRun (trazabilidad de ejecuciones de agente/workflow)
- Modelo MetricEvent (métricas básicas)
- Endpoint `/api/actions/` para listar acciones del usuario actual
- Endpoint `/api/metrics/` (solo Administrador y Usuario IC)
- Página de acciones (template básico con listado)
- Registro automático de trazabilidad en cada llamada a `/api/chat/`

#### spec 5 — rag-mails-dataset-permissions

- Cargar/indexar `mails/output/relevamiento_enriquecido.json` (índice JSONL compacto o SQLite FTS5)
- Filtro de permisos ANTES de armar contexto: bloquear destinatarios restringidos para "Usuario"
- Endpoint/workflow n8n que responde con contexto relevante + respuesta generada
- Integración con orquestador (intención: consulta_historial_mails)
- Reglas de vigencia (0-6 meses vigente, 6-18 aclarar, 18+ desactualizada)
- Trazabilidad obligatoria

#### spec 6 — trigger-comunicaciones-email

- Modelo Proyecto (id, solicitante, brief, audiencia, canal, estado, Focus, aprobadores, etc.)
- Workflow n8n con los 26 pasos del brief sección 22 (MVP 1: solo e-mail)
- Integración con orquestador (intención: generar_plan_comunicacion)
- Brief optimization + preguntas para completar datos faltantes
- Trazabilidad obligatoria

#### spec 7 — contenido-heredado-y-navegacion

- Servir contenido de `comustock-base/` como archivos estáticos
- Rutas Django para Stock, Templates, Mi firma, Toolbox, Roadmap
- Menú lateral funcional (colapsable, un solo menú activo a la vez)
- Carousel de atajos con los 8 accesos del brief sección 13
- Placeholders/estados vacíos para secciones no implementadas en MVP 1

#### spec 8 — memoria-feedback-correcciones

- Modelo UserMemory (memoria conversacional por usuario)
- Toggle de memoria en perfil de usuario
- Modelo AgentFeedback (feedback del usuario sobre respuestas del agente)
- Modelo CorrectionRecord (correcciones aplicadas por el usuario)
- Endpoint para enviar feedback/corrección
- Trazabilidad de feedback y correcciones

#### spec 9 — documentacion-local-y-limites-mvp

- README.md con instalación local paso a paso
- Documentación de límites MVP 1
- Qué está simulado/mockeado
- Dependencias externas (n8n, Gemini API, etc.)
- Documentación de estructura de carpetas

---

## 6. ORDEN DE IMPLEMENTACIÓN

### 6.1 Tabla de dependencias

| Spec                              | Depende de                                              | Por qué                                                                             |
| --------------------------------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| base-django-login-home            | —                                                       | Es la base; nada se construye antes.                                                |
| usuarios-demo-perfiles-permisos   | base-django-login-home                                  | Necesita sesión y login para asociar perfil al usuario logueado.                    |
| home-chat-orchestrator-contract   | usuarios-demo-perfiles-permisos                         | El contrato de entrada lleva `profile`, `roles` y `memory_enabled` del usuario.     |
| acciones-trazabilidad-metricas    | home-chat-orchestrator-contract                         | No hay qué trazar sin que exista una ejecución de orquestador.                      |
| rag-mails-dataset-permissions     | usuarios-demo-perfiles-permisos                         | El filtro de permisos necesita el modelo de perfil/rol ya definido.                 |
| rag-mails-dataset-permissions     | home-chat-orchestrator-contract                         | Se invoca como agente desde el orquestador.                                         |
| rag-mails-dataset-permissions     | acciones-trazabilidad-metricas                          | Trazabilidad obligatoria de toda ejecución de agente (per security-permissions.md). |
| trigger-comunicaciones-email      | home-chat-orchestrator-contract                         | Se dispara como agente desde el orquestador.                                        |
| trigger-comunicaciones-email      | acciones-trazabilidad-metricas                          | Cada proyecto de comunicación debe quedar trazado.                                  |
| contenido-heredado-y-navegacion   | base-django-login-home                                  | Depende de que exista layout y menú lateral.                                        |
| contenido-heredado-y-navegacion   | usuarios-demo-perfiles-permisos _(pendiente confirmar)_ | Solo si el contenido heredado se filtra por perfil.                                 |
| memoria-feedback-correcciones     | usuarios-demo-perfiles-permisos                         | El toggle de memoria es por usuario.                                                |
| memoria-feedback-correcciones     | acciones-trazabilidad-metricas                          | Feedback y correcciones deben quedar trazados.                                      |
| documentacion-local-y-limites-mvp | todos los anteriores                                    | Cierre; documenta lo ya implementado.                                               |

### 6.2 Secuencia serializada recomendada

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

**Regla de paralelismo**: rag-mails-dataset-permissions y trigger-comunicaciones-email
pueden desarrollarse en paralelo, pero ninguna puede empezar antes de que
home-chat-orchestrator-contract Y acciones-trazabilidad-metricas estén completados.
No correr "Run all Tasks" sobre specs que aún no tienen su dependencia directa en estado completed.

---

## 7. PREGUNTA PENDIENTE AL USUARIO

Antes de cerrar el spec maestro, se requiere confirmación sobre el siguiente punto:

> **¿El contenido heredado de Comustock (logos, manuales de marca, templates, etc.)
> se filtra por perfil de usuario, o es accesible para todos los usuarios autenticados?**

- **Si se filtra**: `contenido-heredado-y-navegacion` depende también de
  `usuarios-demo-perfiles-permisos` y debe ser Standard Feature Spec
- **Si NO se filtra**: `contenido-heredado-y-navegacion` solo depende de
  `base-django-login-home` y puede ser Quick Plan

Esta pregunta está marcada como abierta en el template `personal-stock-mvp-master-TEMPLATE.md`
y debe resolverse antes de iniciar el spec 7.

---

_Fin del documento. Para retomar: ver PROGRESO.md y specs en .kiro/specs/._
