# Devolución 128 — Validación acciones-trazabilidad-metricas, tarea 14.1

**Fecha:** 2026-07-01
**Spec:** acciones-trazabilidad-metricas
**Tarea:** 14.1 — Write model tests in core/tests.py

## Qué se implementó

Se agregaron dos clases de test al final de `app/core/tests.py` (después de
`ChatViewTraceabilityIntegrationTest`), siguiendo el mismo estilo que las clases
de test ya existentes para este spec (`TraceabilityManagerTest`,
`MetricsAggregatorTest`, etc.):

- `WorkflowRunModelTest`:
  - `test_workflow_run_indexes_exist`
  - `test_add_state_transition_updates_history`
- `MetricEventModelTest`:
  - `test_metric_event_defaults`

También se agregó el import `from core.models import MetricEvent` junto al
bloque de imports de este spec (cerca de `MetricsAggregator`), ya que `MetricEvent`
no estaba importado todavía en `core/tests.py`.

No se modificó `core/models.py`, `core/views.py`, `core/services.py` ni ningún
template — la tarea es puramente de tests sobre modelos ya existentes.

## Validación criterio por criterio (tasks.md, tarea 14.1)

| Criterio | Estado | Evidencia |
|---|---|---|
| test_workflow_run_indexes_exist: inspect `_meta.indexes`, verify all 4 indexes present | Sí | `app/core/tests.py` (clase `WorkflowRunModelTest`, método `test_workflow_run_indexes_exist`); test corrido con `python -Wa manage.py test core.tests.WorkflowRunModelTest.test_workflow_run_indexes_exist` → `ok` |
| test_add_state_transition_updates_history: create WorkflowRun, call add_state_transition('running'), verify state_history and final_state updated | Sí | `app/core/tests.py` (clase `WorkflowRunModelTest`, método `test_add_state_transition_updates_history`); test corrido → `ok` |
| test_metric_event_defaults: create MetricEvent without value/metadata, verify defaults | Sí | `app/core/tests.py` (clase `MetricEventModelTest`, método `test_metric_event_defaults`); test corrido → `ok` |
| Requirement 1.1 (WorkflowRun con campos e índices estructurados) | Sí | Índices `(user, -created_at)`, `final_state`, `selected_agent`, `created_at` verificados contra `WorkflowRun._meta.indexes` en `app/core/models.py:161-166` |
| Requirement 2.9 (state_history con timestamp en cada transición) | Sí | Assertion `self.assertIn('timestamp', run.state_history[-1])` en el test, contra `add_state_transition()` en `app/core/models.py:171-176` |
| Requirement 8.1 (MetricEvent con campos value y metadata, con defaults) | Sí | Assertions `assertIsNone(event.value)` y `assertEqual(event.metadata, {})` contra `app/core/models.py:200-209` |

## Evidencia de comandos ejecutados

Tests nuevos en aislamiento:
```
python -Wa manage.py test core.tests.WorkflowRunModelTest core.tests.MetricEventModelTest -v 2
...
test_add_state_transition_updates_history ... ok
test_workflow_run_indexes_exist ... ok
test_metric_event_defaults ... ok

Ran 3 tests in 1.318s

OK
```

Suite completa (`core.tests`):
```
python -Wa manage.py test core.tests
...
Ran 148 tests in 540.355s

OK
```

Sin regresiones: 148/148 tests pasan (123 reportados en devolución 119 + tests
agregados en tareas intermedias 11.x/12.x/13.1 no reflejados en esa devolución
anterior + los 3 nuevos de esta tarea).

Nota de entorno: los tests se corrieron con `DJANGO_SECRET_KEY` y `DATABASE_URL`
provistos ad-hoc en el comando (valor dummy y sqlite en memoria vía runner de
Django), sin leer el contenido de `.env` real, conforme a
`security-permissions.md` ("Nunca leer ni mostrar el contenido de .env real").

## Cambio adicional

Ninguno. No se detectaron bugs ni criterios fallidos durante la implementación
o verificación de esta tarea.

## Alcance respetado

- No se tocaron templates.
- No se renombró el producto.
- No se inventaron endpoints ni workflows fuera del spec.
- No se avanzó a la tarea 14.2 (template tests).
- Único archivo de código modificado: `app/core/tests.py` (import + 2 clases de test nuevas).

## Veredicto

Pendiente de validación por Kiro contra `requirements.md` y `tasks.md`. No se
marca la tarea como completed en este documento ni se realiza commit todavía,
conforme al protocolo de CLAUDE.md.
