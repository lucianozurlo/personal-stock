# Devolución 95 — Tarea 12.1: Preparar entorno de testing manual

**Spec:** home-chat-orchestrator-contract
**Tarea:** 12.1 — Preparar entorno de testing
**Fecha:** 2026-06-27
**Estado:** COMPLETED — validación Kiro OK

---

## Qué se ejecutó

Tarea operacional (sin cambios de código). Se verificó el estado del entorno y se ejecutaron los pasos de preparación para el bloque de Testing Manual End-to-End.

---

## Resultados por criterio

### Criterio 1: Verificar que n8n está corriendo en localhost:5678

**Estado:** n8n NO disponible (documentado, escenario válido)
**Evidencia:**

```
curl -s -o /dev/null -w "%{http_code}" http://localhost:5678
→ 000 (sin respuesta — n8n no está corriendo)
```

**Acción:** Documentado. La tarea 12.2 contempla explícitamente este escenario: "Si n8n NO está corriendo, verificar que se muestra error claro 503". El testing manual de 12.2 procederá verificando el comportamiento de error.

---

### Criterio 2: Cargar usuarios demo — `python manage.py load_demo_users`

**Estado:** ✅ Ejecutado con éxito
**Comando ejecutado:**

```bash
python3 manage.py load_demo_users --fixture fixtures/demo_users.json
```

**Output:**

```
Carga exitosa: 100 usuarios cargados.
```

Nota: El comando requiere `--fixture fixtures/demo_users.json` o `--csv <path>` (parámetro obligatorio según su interfaz).

---

### Criterio 3: Iniciar servidor Django — `python manage.py runserver`

**Estado:** ✅ Iniciado sin errores
**Comando:**

```bash
python3 manage.py runserver 127.0.0.1:8000
```

**Log de inicio:**

```
Watching for file changes with StatReloader
[27/Jun/2026 18:53:37] "GET / HTTP/1.1" 302 0
[27/Jun/2026 18:53:37] "GET /api/chat/ HTTP/1.1" 302 0
[27/Jun/2026 18:53:37] "GET /login/ HTTP/1.1" 200 3980
```

Sin ImportError, sin traceback, sin errores de arranque.

---

### Criterio 4: Abrir navegador en localhost:8000

**Estado:** ✅ Endpoint responde correctamente
**Evidencia (curl equivalente):**

```
curl http://127.0.0.1:8000/        → HTTP 302 (redirect a /login/)
curl http://127.0.0.1:8000/login/  → HTTP 200 (página de login OK)
```

Comportamiento esperado: el home redirige a login porque el usuario no está autenticado.

---

### Verificación adicional: /api/chat/ requiere autenticación

```
curl http://127.0.0.1:8000/api/chat/ → HTTP 302 (redirect a login por @login_required)
```

El endpoint de chat está correctamente protegido.

---

## Resumen

| Criterio                         | Estado                      | Evidencia                               |
| -------------------------------- | --------------------------- | --------------------------------------- |
| n8n en localhost:5678 verificado | No disponible (documentado) | curl → 000, sin respuesta               |
| `load_demo_users` ejecutado      | ✅ Exitoso                  | "Carga exitosa: 100 usuarios cargados." |
| `runserver` iniciado             | ✅ Exitoso                  | PID 33877, log sin errores              |
| localhost:8000 responde          | ✅ HTTP 302                 | curl → 302 redirect a /login/           |

**Entorno listo para tarea 12.2.** n8n no disponible → el testing de 12.2 cubrirá el escenario "n8n down → error 503".

---

## Validación Kiro

**Veredicto:** COMPLETED

**Análisis:**

Todos los criterios de la tarea 12.1 "Preparar entorno de testing" se cumplieron:

1. ✅ n8n verificado (no disponible, escenario válido documentado en tasks.md como opcional)
2. ✅ Usuarios demo cargados exitosamente (100 usuarios)
3. ✅ Servidor Django iniciado sin errores
4. ✅ Endpoint localhost:8000 responde correctamente (HTTP 302 → /login/, protección de auth funciona)

La ausencia de n8n NO es un bloqueante. La tarea 12.2 contempla explícitamente este escenario para verificar el manejo de errores.

**Próximo paso:** Tarea 12.2 — Ejecutar checklist de testing manual
