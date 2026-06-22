# Validación — spec: usuarios-demo-perfiles-permisos — Tarea 1.1

**Fecha:** 2026-06-22
**Spec:** usuarios-demo-perfiles-permisos
**Tarea:** 1.1 — Crear script de backup del superusuario actual
**Estado:** ✅ COMPLETED — Validación Kiro OK

---

## Qué se implementó

Se creó la estructura de management commands de Django y el comando `backup_superuser` que extrae los datos del superusuario actual y los guarda en `app/fixtures/superuser_backup.json`.

### Archivos creados

- `app/core/management/__init__.py` — paquete Python (vacío)
- `app/core/management/commands/__init__.py` — paquete Python (vacío)
- `app/core/management/commands/backup_superuser.py` — management command
- `app/fixtures/superuser_backup.json` — backup generado al ejecutar el comando

---

## Verificación punto por punto

| Criterio de aceptación (tasks.md)                                                  | Estado      | Evidencia                                                                                                                                                   |
| ---------------------------------------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Script extrae email, password hash, is_staff, is_superuser del superusuario actual | ✅ cumplido | `superuser_backup.json` contiene los 4 campos más first_name y last_name                                                                                    |
| Guardar backup en `app/fixtures/superuser_backup.json`                             | ✅ cumplido | Archivo existe en la ruta exacta; output del comando: `Backup guardado en .../app/fixtures/superuser_backup.json — email: test@personal.com.ar`             |
| Documentar en código que este backup se usará después de la migración              | ✅ cumplido | Docstring en `backup_superuser.py` líneas 1-8: "El backup generado en fixtures/superuser_backup.json se usará en tarea 3.3 para recrear el superusuario..." |

---

## Contenido del backup generado

```json
{
  "email": "test@personal.com.ar",
  "password": "pbkdf2_sha256$1000000$dfClIl6G2mYbTDF12YTGEJ$KW57w2x7UpQfVe138MUTEaFlq/u9aBBJilonolYVESE=",
  "first_name": "Luciano",
  "last_name": "Prueba",
  "is_staff": true,
  "is_superuser": true
}
```

Password hasheado con PBKDF2-SHA256 (Django default). No se expone el hash raw ni credencial en texto claro.

---

## Comando ejecutado

```bash
cd app && DJANGO_SECRET_KEY=change-me-dev-only DATABASE_URL=sqlite:///db.sqlite3 python3 manage.py backup_superuser
# Output: Backup guardado en /Users/luciano/Desktop/PS-edit/app/fixtures/superuser_backup.json — email: test@personal.com.ar
```

---

## Validación Kiro

### Verificación contra tasks.md

✅ **Todos los criterios de aceptación cumplidos:**

1. Script extrae email, password hash, is_staff, is_superuser (líneas 31-37 de backup_superuser.py)
2. Backup guardado en `app/fixtures/superuser_backup.json` (archivo existe, ruta correcta)
3. Documentación en código sobre uso futuro en tarea 3.3 (docstring líneas 1-8)

### Verificación contra requirements.md

La tarea 1.1 es preparatoria y no mapea directamente a requirements funcionales específicos, pero cumple con el **contexto crítico del spec**: "este spec corre DESPUÉS de base-django-login-home, lo que significa que ya existe un superusuario creado en la base de datos. La migración a AbstractUser requiere preservar o recrear ese superusuario para no perder acceso al sistema."

✅ **El script preserva correctamente:**

- Email único del superusuario
- Password hash (sin exposición de credenciales)
- Flags is_staff y is_superuser
- Datos adicionales (first_name, last_name)

### Hallazgos

**Positivo:**

- Estructura de management commands correctamente creada
- Manejo de errores: si no hay superusuario, termina con SystemExit(1)
- Output claro y descriptivo
- Ruta de fixtures creada automáticamente si no existe
- Encoding UTF-8 y formato JSON legible

**Ningún conflicto ni bug detectado.**

---

## Veredicto Final

**✅ COMPLETED**

La tarea 1.1 cumple todos los criterios de aceptación de tasks.md. El backup del superusuario está guardado correctamente y listo para usarse en tarea 3.3 (recrear superusuario después de migración a Custom User Model).

**Actualización de estado:**

- ✅ tasks.md: tarea 1.1 marcada como [x]
- ✅ PROGRESO.md actualizado: spec actual = usuarios-demo-perfiles-permisos, tarea actual = 2.1
- ✅ Historial de validaciones Kiro: entrada agregada para tarea 1.1

**Next:** Implementar tarea 2.1 con Claude Code (sesión nueva)
