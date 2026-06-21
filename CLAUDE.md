# Personal Stock workflow

## Fuente de reglas (leer primero, siempre)
Antes de tocar cualquier archivo, leé estos steering files completos. Son la fuente
única de reglas de producto, técnicas, de estructura y de seguridad — este archivo
NO las repite para evitar que queden desincronizadas:

@.kiro/steering/product.md
@.kiro/steering/tech.md
@.kiro/steering/structure.md
@.kiro/steering/security-permissions.md
@.kiro/steering/rules.md

## Reglas específicas de esta sesión (no están en el steering)
- Nunca implementes más de una tarea de .kiro/specs/* por sesión.
- Antes de editar, leé requirements.md, design.md y tasks.md del spec vigente.
- No toques archivos fuera del alcance explícito de la tarea.
- No marques una tarea como completed vos mismo. Reportá el resultado y esperá a que
  se valide contra tasks.md desde Kiro antes de que se considere cerrada.
- No hagas commit hasta que la tarea esté validada.

## Commands
- Desarrollo: python manage.py runserver 127.0.0.1:8000
- Tests: python -Wa manage.py test
- Fixtures: python manage.py loaddata fixtures/demo_users.json
- Migraciones: python manage.py makemigrations && python manage.py migrate

## Task protocol
1. Resumí el plan antes de tocar nada.
2. Listá archivos a tocar (deben estar dentro del alcance declarado en el prompt).
3. Editá.
4. Corré los tests/comandos indicados en el criterio de aceptación.
5. Compará el resultado contra el criterio de aceptación de tasks.md, explícitamente,
   punto por punto.
6. Resumí el diff (archivos modificados, líneas clave).
7. Reportá tarea [ID] como una lista, un ítem por cada criterio de aceptación
   de tasks.md para esa tarea: criterio → cumplido (sí/no/parcial) → evidencia
   concreta (archivo+línea, output de test, o comando corrido). No cierres con
   un veredicto único global del estilo "tarea X: sí" — cada criterio se valida
   por separado. Detené ahí. No avances a la siguiente tarea ni hagas commit
   todavía.

## Después del reporte (lo hace el humano, volviendo a Kiro)
- Pedirle a Kiro que valide el resultado contra requirements.md y tasks.md.
- Si Kiro confirma, recién ahí pedirle a Claude Code que haga el commit:
  git add <archivos> && git commit -m "tipo(spec-id): descripción — tarea X.Y"
- Si Kiro no confirma, volver al punto 1 con las correcciones indicadas por Kiro,
  todavía dentro de la misma tarea.

## Naming de commits
feat|fix|test|docs(spec-id): descripción breve — tarea X.Y

Ejemplos:
feat(base-django-login-home): login con template y sesión — tarea 1.2
test(rag-mails-dataset-permissions): tests de bloqueo por perfil — tarea 3.1
