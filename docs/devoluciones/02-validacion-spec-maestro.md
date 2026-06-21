# VALIDACIÓN DEL SPEC MAESTRO — Personal Stock MVP

> Documento de validación generado por Kiro tras aplicar decisiones del Paso 2 (RUNBOOK.md).
> Fecha: 2026-06-21
> Estado: spec maestro generado y validado

---

## 1. QUÉ SE PERSISTIÓ

### 1.1 Archivo generado

✅ **Spec maestro creado en**: `.kiro/specs/personal-stock-mvp-master/requirements.md`

**Formato**: Solo requirements.md (sin design.md ni tasks.md) porque el spec maestro es un documento coordinador, no un spec de implementación.

**Contenido**:

- Lista de 9 specs con tipo (Standard Feature / Quick Plan)
- Tabla de dependencias completa (13 filas)
- Secuencia de implementación recomendada
- Alcance detallado por spec
- Decisiones consolidadas (6 decisiones ya tomadas)
- Riesgos identificados (3 riesgos abiertos)
- Regla de paralelismo
- Columna de Estado por spec (todas en "sin empezar")

### 1.2 Estructura respetada

✅ **Los 9 specs del inventario-diagnóstico se mantuvieron tal como estaban**:

| #   | Spec                              | Tipo Inventario                       | Tipo Spec Maestro                     | ✓   |
| --- | --------------------------------- | ------------------------------------- | ------------------------------------- | --- |
| 1   | base-django-login-home            | Standard Feature (Requirements-first) | Standard Feature (Requirements-first) | ✅  |
| 2   | usuarios-demo-perfiles-permisos   | Standard Feature (Requirements-first) | Standard Feature (Requirements-first) | ✅  |
| 3   | home-chat-orchestrator-contract   | Standard Feature (Requirements-first) | Standard Feature (Requirements-first) | ✅  |
| 4   | acciones-trazabilidad-metricas    | Standard Feature (Requirements-first) | Standard Feature (Requirements-first) | ✅  |
| 5   | rag-mails-dataset-permissions     | Standard Feature (Requirements-first) | Standard Feature (Requirements-first) | ✅  |
| 6   | trigger-comunicaciones-email      | Standard Feature (Requirements-first) | Standard Feature (Requirements-first) | ✅  |
| 7   | contenido-heredado-y-navegacion   | Quick Plan (ver nota\*)               | Quick Plan                            | ✅  |
| 8   | memoria-feedback-correcciones     | Standard Feature (Requirements-first) | Standard Feature (Requirements-first) | ✅  |
| 9   | documentacion-local-y-limites-mvp | Quick Plan                            | Quick Plan                            | ✅  |

**Nota sobre spec 7**: En el inventario-diagnóstico quedó pendiente si el contenido heredado
se filtraba por perfil. La decisión fue: **NO se filtra, acceso amplio**. Por lo tanto,
el spec 7 es Quick Plan y solo depende de `base-django-login-home`.

### 1.3 Tabla de dependencias respetada

✅ **Las 13 filas de la tabla de dependencias del inventario-diagnóstico se conservaron íntegramente**:

Todas las dependencias del template (sección 6.1 del inventario) fueron trasladadas al spec
maestro sin cambios, excepto:

- ✅ Se resolvió la nota pendiente del spec 7: solo depende de `base-django-login-home`
  (no de `usuarios-demo-perfiles-permisos`) porque el contenido heredado NO se filtra.
- ✅ Se corrigió un typo en el inventario: "home-chat-orchestrador-contract" → "home-chat-orchestrator-contract"

### 1.4 Secuencia de implementación respetada

✅ **La secuencia serializada recomendada del inventario (sección 6.2) se mantuvo**:

```
1. base-django-login-home
2. usuarios-demo-perfiles-permisos
3. home-chat-orchestrator-contract
4. acciones-trazabilidad-metricas
5a. rag-mails-dataset-permissions    ─┐ paralelo posible
5b. trigger-comunicaciones-email     ─┘
6. contenido-heredado-y-navegacion
7. memoria-feedback-correcciones
8. documentacion-local-y-limites-mvp
```

---

## 2. DECISIONES APLICADAS

### 2.1 Decisión: Home → home.html (renombrado)

**Contexto**: El archivo fuente se llama `templates/index.html`, pero el brief lo menciona como `home.html`. La sección 1.3 del inventario identificó esta discrepancia.

**Resolución aplicada**:

- El spec maestro incorpora como **Decisión 1**: renombrar `templates/index.html` → `templates/home.html` en la primera tarea del spec 1.
- Todas las referencias en specs, steering files y código apuntan a `home.html`.
- Esta decisión está documentada en la sección "Decisiones Consolidadas" del spec maestro.
- Impacto: La tarea de renombrado debe ejecutarse en el spec `base-django-login-home`.

**Estado**: ✅ Documentado, NO es riesgo abierto.

### 2.2 Decisión: Assets de templates

**Contexto**: Los assets de templates están distribuidos en subdirectorios (css/, js/, img/).

**Resolución aplicada**:

- El spec maestro incorpora como **Decisión 2**: las rutas oficiales son:
  - Estilos: `templates/css/`
  - Scripts: `templates/js/`
  - Logos: `templates/img/`
- Impacto: `STATICFILES_DIRS` en Django debe incluir estas rutas.
- Esta decisión está documentada en la sección "Decisiones Consolidadas" del spec maestro.

**Estado**: ✅ Documentado, NO es riesgo abierto.

### 2.3 Decisión: Dataset indexado, no carga completa

**Contexto**: `relevamiento_enriquecido.json` tiene ~5.300 registros (~169k líneas). El riesgo 2.3 del inventario identificó que cargar todo en memoria por consulta es lento.

**Resolución aplicada**:

- El spec maestro incorpora como **Decisión 3**: crear índice compacto JSONL o usar SQLite FTS5, cargar en memoria al inicio (caching simple).
- Impacto: El spec 5 (`rag-mails-dataset-permissions`) debe incluir tarea de indexación/caching, no lectura directa del JSON completo.
- Esta decisión está documentada en la sección "Decisiones Consolidadas" del spec maestro.
- El riesgo original fue **cerrado** y reemplazado por una decisión de implementación.

**Estado**: ✅ Documentado, NO es riesgo abierto.

### 2.4 Decisión: Reemplazo de "Benja" hardcodeado

**Contexto**: El riesgo 2.2 del inventario identificó que "Benja" aparece hardcodeado en:

- `templates/index.html` (ahora `home.html`): `<span id="welcomeTitle">Hola, Benja.</span>`
- `templates/js/app.js`: array `RANDOM_GREETINGS` con "Hola Benja!"

**Resolución aplicada**:

- El spec maestro incorpora como **Decisión 4**: reemplazar solo en `templates/` y `./app/` (NO tocar `cs-chat-rag/`):
  - En `home.html`: usar template tag Django `{{ user.first_name }}`.
  - En `app.js`: obtener `userId` desde sesión Django (endpoint `/api/me/` o contexto embebido).
- Impacto: El spec 1 (`base-django-login-home`) debe incluir tarea explícita de reemplazo.
- Esta decisión está documentada en la sección "Decisiones Consolidadas" del spec maestro.
- El riesgo original fue **cerrado** y reemplazado por una tarea de implementación.

**Estado**: ✅ Documentado, NO es riesgo abierto.

### 2.5 Decisión: DATABASE_URL cableada con dj-database-url

**Contexto**: La sección 1.6 del inventario identificó que `.env.example` declara `DATABASE_URL` pero la dependencia `dj-database-url` no está instalada. El steering file `tech.md` exige cableo real de toda variable de entorno declarada.

**Resolución aplicada**:

- El spec maestro incorpora como **Decisión 5**: la primera tarea del spec 1 (bootstrap Django) debe:
  1. Instalar `dj-database-url` en `requirements.txt`
  2. Cablearla en `settings.py`: `DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])`
- Impacto: Ninguna tarea se considera completa si declara una variable de entorno sin cableo real en código (per tech.md).
- Esta decisión está documentada en la sección "Decisiones Consolidadas" del spec maestro.

**Estado**: ✅ Documentado, NO es riesgo abierto.

### 2.6 Decisión: Contenido heredado de Comustock — acceso amplio

**Contexto**: La sección 7 del inventario-diagnóstico dejó abierta la pregunta: "¿El contenido heredado de Comustock se filtra por perfil de usuario, o es accesible para todos los usuarios autenticados?"

**Resolución aplicada (decisión del usuario)**:

- **Respuesta**: el contenido heredado de Comustock es de acceso amplio para todo usuario autenticado. **NO se filtra por perfil**.
- Impacto:
  - El spec 7 (`contenido-heredado-y-navegacion`) es **Quick Plan** (no Standard Feature).
  - Solo depende de `base-django-login-home` (no de `usuarios-demo-perfiles-permisos`).
  - La tabla de dependencias del spec maestro refleja esta decisión (fila del spec 7 solo lista `base-django-login-home` como dependencia).
- Esta decisión está documentada en la sección "Decisiones Consolidadas" del spec maestro.
- La pregunta del inventario fue **resuelta y cerrada**.

**Estado**: ✅ Documentado, pregunta resuelta.

---

## 3. RIESGOS TRASLADADOS (ABIERTOS)

Los siguientes riesgos del inventario-diagnóstico NO fueron resueltos con las decisiones del usuario. Se trasladaron al spec maestro como **riesgos abiertos** que requieren mitigación durante la implementación:

### Riesgo 1: Compatibilidad cs-chat-rag ↔ Django

**Origen**: Riesgo 2.1 del inventario-diagnóstico
**Severidad**: ALTA
**Mitigación planificada**:

1. Crear `./app` Django desde cero.
2. Reutilizar SOLO: schema PostgreSQL de memoria conversacional, patrón de orquestación n8n, inspiración UI.
3. NO importar `cs-chat-rag` como módulo Python.
4. Documentar explícitamente qué se hereda y qué se reescribe.

**Documentado en**: specs 1, 3 y 8.

### Riesgo 2: n8n no disponible localmente

**Origen**: Riesgo 2.4 del inventario-diagnóstico
**Severidad**: MEDIA
**Mitigación planificada** (per tech.md):

1. Crear función/vista Django mock que reciba el mismo payload del webhook n8n.
2. Responder con JSON coherente con el contrato de salida del brief (sección 8).
3. Marcar trazabilidad como `simulado: true`.
4. Dejar `TODO` explícito en código.

**Documentado en**: spec `home-chat-orchestrator-contract` (tarea de fallback mock).

### Riesgo 3: Campos del dataset que el brief asume pero no existen

**Origen**: Riesgo 2.6 del inventario-diagnóstico
**Severidad**: BAJA
**Mitigación planificada** (per rules.md): ante conflicto entre brief y estructura real, **frenar y preguntar**. Señalar discrepancia exacta, proponer 1-2 alternativas, documentar decisión en spec.

**Documentado en**: spec `rag-mails-dataset-permissions`.

---

## 4. RIESGOS CERRADOS (REEMPLAZADOS POR DECISIONES)

Los siguientes riesgos del inventario-diagnóstico fueron **cerrados** porque el usuario proporcionó decisiones concretas que los resuelven:

### Riesgo 2.2 cerrado → Decisión 4

**Riesgo original**: Templates con usuario hardcodeado "Benja"
**Resolución**: Decisión 4 del spec maestro — reemplazar en templates/ y app/.
**Estado**: ✅ Cerrado.

### Riesgo 2.3 cerrado → Decisión 3

**Riesgo original**: Volumen del dataset histórico
**Resolución**: Decisión 3 del spec maestro — usar índice compacto o SQLite FTS5.
**Estado**: ✅ Cerrado.

### Riesgo 2.5 cerrado → Decisiones 1 y 2

**Riesgo original**: Discrepancias brief ↔ realidad
**Resolución**: Decisiones 1 (home.html) y 2 (assets de templates) del spec maestro.
**Estado**: ✅ Cerrado.

---

## 5. VERIFICACIÓN DE INTEGRIDAD

### 5.1 Checklist del template

El template `personal-stock-mvp-master-TEMPLATE.md` pedía explícitamente:

| Elemento requerido                      | ¿Presente en spec maestro?    | ✓   |
| --------------------------------------- | ----------------------------- | --- |
| Lista de specs y orden sugerido         | ✅ Sí (tabla completa)        | ✅  |
| Tabla de dependencias (obligatoria)     | ✅ Sí (13 filas)              | ✅  |
| Regla de paralelismo                    | ✅ Sí (sección dedicada)      | ✅  |
| Qué specs usan Standard vs Quick Plan   | ✅ Sí (tabla + justificación) | ✅  |
| Riesgos a listar explícitamente         | ✅ Sí (3 riesgos abiertos)    | ✅  |
| Columna de estado por spec (sugerencia) | ✅ Sí (columna "Estado")      | ✅  |

### 5.2 Alcance detallado por spec

El spec maestro incluye una sección "Alcance Detallado por Spec" con bullet points del inventario-diagnóstico (sección 5) para cada uno de los 9 specs. Esto facilita el arranque de cada spec hijo sin tener que releer el inventario completo.

### 5.3 Decisiones vs. riesgos: separación clara

El spec maestro separa claramente:

- **Decisiones Consolidadas** (6 decisiones ya tomadas, NO son riesgos abiertos)
- **Riesgos Identificados** (3 riesgos abiertos que requieren mitigación durante implementación)

Esto evita confusión sobre qué está resuelto y qué sigue pendiente.

---

## 6. CONFIRMACIÓN DE NO REINTERPRETACIÓN

✅ **Los 9 specs del inventario se mantuvieron intactos**: ningún spec fue fusionado, dividido, renombrado o eliminado.

✅ **Los tipos (Standard / Quick Plan) se mantuvieron**: excepto el spec 7, que se confirmó como Quick Plan tras resolver la pregunta pendiente.

✅ **La tabla de dependencias se mantuvo**: todas las filas del inventario se trasladaron sin cambios (solo se corrigió un typo: "orchestrador" → "orchestrator").

✅ **La secuencia de implementación se mantuvo**: el orden serializado recomendado del inventario (sección 6.2) se copió íntegramente.

---

## 7. PRÓXIMOS PASOS

Con el spec maestro validado, el flujo de trabajo continúa según RUNBOOK.md:

1. **Paso 3.1 — Crear spec hijo**: El usuario elige qué spec implementar primero (recomendado: spec 1, `base-django-login-home`).
2. **Paso 3.2 — Generar requirements/design/tasks**: Según el tipo del spec (Standard Feature → requirements primero; Quick Plan → directo a tasks).
3. **Paso 3.3 — Gate de aprobación**: Kiro valida que el spec hijo cumpla criterios de format, coherencia y steering antes de pasar a implementación.
4. **Paso 3.4 — Implementación con Claude Code**: Una tarea por sesión, validación de Kiro al cierre de cada tarea.
5. **Paso 3.5 — Actualizar estado en spec maestro**: Al completar cada tarea o fase, actualizar la columna "Estado" en la tabla "Lista de Specs" del spec maestro.

---

## VEREDICTO FINAL

**Estado**: ✅ **SPEC MAESTRO VALIDADO Y APROBADO**

**Fecha**: 2026-06-21

**Confirmaciones**:

- ✅ Los 9 specs del inventario se respetaron íntegramente (sin reinterpretación)
- ✅ La tabla de dependencias se trasladó completa (13 filas)
- ✅ La secuencia de implementación se mantuvo
- ✅ Las 6 decisiones del usuario se incorporaron como "Decisiones Consolidadas"
- ✅ Los 3 riesgos abiertos se trasladaron con mitigaciones planificadas
- ✅ Los riesgos resueltos (2.2, 2.3, 2.5) se cerraron y reemplazaron por decisiones
- ✅ La pregunta pendiente del inventario (sección 7) se resolvió: contenido heredado NO se filtra
- ✅ La columna de Estado por spec está presente (todas en "sin empezar")
- ✅ El spec maestro está listo para coordinar la implementación de los 9 specs hijos

**Archivo persistido**: `.kiro/specs/personal-stock-mvp-master/requirements.md`

**Siguiente acción recomendada**: Iniciar el spec 1 (`base-django-login-home`) con workflow Requirements-First.

---

_Fin de la validación. Personal Stock MVP — spec maestro generado y listo para uso._
