---
inclusion: always
---

# Stack y restricciones técnicas

## Stack base
- Python / Django
- Frontend basado en templates HTML existentes (no framework JS pesado en MVP 1)
- n8n como orquestador de workflows
- Gemini como LLM inicial
- Almacenamiento local para MVP 1
- SQLite por defecto para desarrollo local si no se especifica otra cosa

## Reglas de implementación
- Crear la app Django dentro de ./app para aislarla del material heredado del workspace root.
- Antes de scaffoldear nada, inspeccionar cs-chat-rag e indicar si ya es un proyecto Django,
  Flask, o solo scripts sueltos, y si ya tiene lógica de RAG implementada. No crear estructura
  nueva que duplique una base existente sin dejarlo explícito en el inventario.
- Mantener templates fuente en ./templates (raíz del workspace, NO dentro de ./app) y
  conectarlos por configuración de Django: agregar la carpeta a TEMPLATES[0]['DIRS'] en
  settings.py usando una ruta absoluta vía BASE_DIR.parent, y agregar STATICFILES_DIRS
  para los SVG de logo. Esta ruta debe coincidir siempre con structure.md — si hay
  discrepancia entre steering files, structure.md es la fuente de verdad sobre rutas.
- Usar variables de entorno para secretos e integraciones. Nunca credenciales reales en el repo.
  No dejar variables de entorno declaradas en .env.example sin uso real cableado en el código
  (ver más abajo "Dependencia explícita: dj-database-url" para el caso de DATABASE_URL).
- Mantener contratos explícitos para Django ↔ n8n, con el esquema de entrada/salida común
  definido en el spec home-chat-orchestrator-contract antes de tocar código de agentes.
- Implementar pruebas mínimas por spec antes de cerrar tareas críticas (permisos, RAG, envío).

## Regla de integración con Claude Code
- Claude Code no define arquitectura, alcance, permisos ni reglas de compliance.
- Claude Code solo implementa tareas ya aprobadas en .kiro/specs/*, una por sesión.
- El modo por defecto de Claude Code para este repo es plan.
- Ninguna tarea se marca completed en tasks.md sin que Kiro valide el resultado contra
  requirements.md y el criterio de aceptación de esa tarea. Claude Code no se autocalifica.

## Control de versiones
- Cada tarea completada y validada genera un commit atómico.
- Formato de mensaje: tipo(spec-id): descripción breve — tarea X.Y
  Ejemplo: feat(base-django-login-home): login con template y sesión — tarea 1.2
- No hacer commits que mezclen tareas de specs distintos.

## Dependencia explícita: dj-database-url
- `.env.example` declara `DATABASE_URL`. La tarea que primero la usa
  (normalmente la tarea 1.1 de `base-django-login-home`, el bootstrap) debe
  instalar `dj-database-url` y cablearla en `settings.py`:
  `DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])`.
- Ninguna tarea se considera completa si declara `DATABASE_URL` (u otra
  variable de entorno) sin ese cableo real en código. Verificarlo
  explícitamente en el reporte de Claude Code antes de validar la tarea
  contra su criterio de aceptación.

## Fallback de n8n para desarrollo local
- `N8N_WEBHOOK_URL` en `.env.example` asume una instancia de n8n corriendo en
  `localhost:5678`. Si n8n no está disponible en el entorno de desarrollo:
  - El contrato de entrada/salida definido en `home-chat-orchestrator-contract`
    se respeta igual — no se cambia el shape de los datos por no tener n8n.
  - Se simula la llamada con una función o vista de Django que reciba el
    mismo payload que recibiría el webhook de n8n y devuelva una respuesta
    de ejemplo coherente con el contrato, dejando un TODO explícito en el
    código y en `tasks.md` que marque que es un mock temporal.
  - La simulación queda trazada igual que una ejecución real
    (ver `security-permissions.md`: trazabilidad obligatoria), marcando el
    resultado o la metadata como `simulado: true` para no confundirla
    después con una ejecución real de n8n.
  - Esto es la aplicación concreta de la regla de `product.md`: "Si una API
    externa no está disponible, se simula o se deja contrato documentado."

## Fuente única de reglas
- .kiro/steering/*.md es la fuente de verdad para reglas de producto, técnicas, de
  estructura, de seguridad y de proceso. CLAUDE.md no debe duplicar estas reglas con
  su propio texto: debe referenciar estos archivos (@.kiro/steering/...) para que
  Claude Code los lea directamente. Si CLAUDE.md y un steering file alguna vez dicen
  cosas distintas sobre lo mismo, gana el steering file y hay que corregir CLAUDE.md.
