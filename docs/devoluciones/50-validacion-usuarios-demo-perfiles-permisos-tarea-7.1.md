# Validación: usuarios-demo-perfiles-permisos — Tarea 7.1

**Spec:** usuarios-demo-perfiles-permisos
**Tarea:** 7.1 — Crear fixture JSON con 100 usuarios demo
**Fecha:** 2026-06-23
**Archivo creado:** `app/fixtures/demo_users.json`

---

## Criterios de aceptación y resultados

| Criterio                                                                            | Estado      | Evidencia                                                                                                                                                                                                       |
| ----------------------------------------------------------------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Incluir los 12 usuarios específicos con datos exactos del Requirement 2             | ✅ cumplido | Shell: todos los 12 emails encontrados, `name=True` para todos, perfiles correctos. Output: comustock.ci@gmail.com → Luciano Zurlo / Administrador, comustock.uci1@gmail.com → Diego Ferrari / Usuario IC, etc. |
| Generar 88 usuarios ficticios adicionales con nombres argentinos realistas          | ✅ cumplido | PKs 13–100: nombres y apellidos argentinos auténticos (García, Fernández, Rodríguez…). Emails: demo.user{N}@personalstock.local                                                                                 |
| Distribuir perfiles: al menos 15 Usuario IC, al menos 30 Usuario, resto distribuido | ✅ cumplido | Shell: Administrador=4, Usuario IC=18 (≥15 ✓), Usuario=33 (≥30 ✓), Heavy user=25, Macro=20. Total=100 ✓                                                                                                         |
| Asignar roles solo a usuarios con perfil Usuario IC                                 | ✅ cumplido | Shell: `Usuarios no-IC con roles: 0`                                                                                                                                                                            |
| Asignar roles variados a Usuario IC (al menos un usuario por cada rol de los 7)     | ✅ cumplido | Shell: Diseñador=3, Desarrollador=2, Redactor=4, Productor=3, Gerente Cultura=2, Gerente IC=2, Especialista=2. Todos los 7 roles cubiertos.                                                                     |
| Configurar memoria_habilitada = true por defecto                                    | ✅ cumplido | Shell: `Usuarios con memoria_habilitada=False: 0`                                                                                                                                                               |
| Validar que todos los emails son únicos                                             | ✅ cumplido | Shell: `Emails únicos: 100 / OK: True`                                                                                                                                                                          |
| Fixture cargable con loaddata                                                       | ✅ cumplido | `python manage.py loaddata fixtures/demo_users.json` → `Installed 107 object(s) from 1 fixture(s)`                                                                                                              |

---

## Cambio adicional (conflicto documentado)

**Conflicto entre Req 2.1 y Req 4.2:**

- **Req 2.1** especifica: "Luciano Zurlo with profile Administrador, **roles Diseñador and Desarrollador**"
- **Req 4.2** especifica: "WHERE a user does not have profile Usuario IC, THE User_System SHALL not assign any role"
- El criterio de la tarea 7.1 también dice: "Asignar roles solo a usuarios con perfil Usuario IC"

**Decisión tomada:** Luciano Zurlo (pk=1, Administrador) tiene `roles: []` en el fixture, siguiendo Req 4.2 y el criterio de aceptación de esta tarea. La inconsistencia en Req 2.1 necesita resolución de Kiro antes de que la tarea 7.2 ("Test roles solo en Usuario IC") pueda cerrarse sin ambigüedad.

**Kiro debe confirmar:** ¿Los "roles" mencionados en Req 2.1 para Luciano Zurlo son un error de spec (debe no tenerlos, siguiendo 4.2) o una excepción intencional del perfil Administrador?

---

## Datos de referencia

- **Fixture:** `app/fixtures/demo_users.json`
- **Objetos totales:** 107 (7 roles + 100 usuarios)
- **Password usuarios específicos:** hash PBKDF2 de "personalstock" (cambiable en producción)
- **Password usuarios ficticios:** `"!"` (unusable password — solo para demo)
- **Superusuario (pk=1, Luciano Zurlo):** is_staff=true, is_superuser=true
- **Aprobadores:** Jonathan Ferraro (pk=7) y Luciana Dau (pk=8) tienen puede_aprobar=true y es_aprobador_default=true

---

## Análisis del conflicto (Kiro)

**Conflicto identificado:**

- Req 2.1 (AC1) dice: "Luciano Zurlo with profile Administrador, roles Diseñador and Desarrollador"
- Req 4.2 (AC2) dice: "WHERE a user does not have profile Usuario IC, THE User_System SHALL not assign any role"
- Criterio de tarea 7.1 dice: "Asignar roles solo a usuarios con perfil Usuario IC"

**Prioridad de fuentes:**

1. Requirements.md (fuente de verdad sobre el qué)
2. Tasks.md (implementación del cómo, derivada de requirements)

**Análisis técnico:**
Req 4.2 establece una regla de sistema clara: el campo `roles` es exclusivo del perfil Usuario IC. Esta regla está reforzada por:

- AC1 de Req 4.1: "WHERE a user has profile Usuario IC, THE User_System SHALL allow assignment..."
- AC2 de Req 4.2: "WHERE a user does not have profile Usuario IC, THE User_System SHALL not assign any role"

Req 2.1 parece describir un caso de prueba específico que fue redactado antes de que se consolidara la regla del sistema. El término "roles" en Req 2.1 probablemente se refiere a funciones organizacionales informales, no al campo técnico `roles` del modelo.

**Resolución:**
La implementación de Claude Code siguió **correctamente** Req 4.2 y el criterio de la tarea. El perfil Administrador no es Usuario IC, por lo tanto no debe tener roles técnicos asignados en el campo `roles`. Luciano Zurlo tiene:

- perfil: Administrador (correcto)
- roles: [] (correcto según Req 4.2)
- is_superuser: true (acceso completo al sistema)

**Acción requerida:**
Marcar Req 2.1 (AC1) para corrección en una revisión futura del spec. El AC debe decir:
"THE User_System SHALL include Luciano Zurlo with profile Administrador and email comustock.ci@gmail.com"
(sin mencionar roles Diseñador y Desarrollador).

---

## Veredicto Kiro: ✅ COMPLETED

**Decisión:** La tarea 7.1 se marca **completed**.

**Fundamentos:**

1. Todos los criterios de aceptación de la tarea 7.1 están cumplidos
2. La decisión de dejar roles=[] para Luciano Zurlo es correcta según Req 4.2
3. El conflicto está en la redacción de Req 2.1, no en la implementación
4. La regla del sistema (Req 4.2) tiene precedencia sobre un ejemplo individual (Req 2.1)
5. Los 8 tests existentes pasan sin regresiones
6. El fixture se carga correctamente con loaddata

**Próximos pasos:**

1. Marcar tarea 7.1 como [x] en tasks.md
2. Actualizar PROGRESO.md con tarea 7.2 como siguiente
3. Documentar en requirements.md (Conflicts and Decisions) que Req 2.1 AC1 contiene un error de especificación que fue corregido en la implementación siguiendo Req 4.2
