# Validación — Tarea 2.1: Custom User Model

**Spec:** usuarios-demo-perfiles-permisos
**Fecha:** 2026-06-22
**Tarea:** 2.1 — Implementar User model extendiendo AbstractUser en `app/core/models.py`

---

## Qué se validó

Implementación del modelo `User` en `app/core/models.py` extendiendo `AbstractUser` con todos los campos y métodos requeridos por el spec.

---

## Hallazgos

### Archivo modificado

- `app/core/models.py` — reemplazado placeholder por clase `User(AbstractUser)` completa

### Verificación de sintaxis

```
python3 -c "import py_compile; py_compile.compile('core/models.py', doraise=True); print('Sintaxis OK')"
→ Sintaxis OK
```

### Criterios de aceptación — revisión punto por punto

| Criterio                                          | Estado | Evidencia (archivo:línea)                                                              |
| ------------------------------------------------- | ------ | -------------------------------------------------------------------------------------- |
| email como EmailField unique (USERNAME_FIELD)     | ✅ sí  | models.py:13 — `email = models.EmailField(unique=True)`                                |
| perfil CharField con 5 Profile choices            | ✅ sí  | models.py:6-11 — TextChoices con Administrador, Usuario IC, Heavy user, Macro, Usuario |
| roles ManyToManyField('Role', blank=True)         | ✅ sí  | models.py:20-25 — referencia string, related_name='users'                              |
| cargo CharField(max_length=100, blank=True)       | ✅ sí  | models.py:26                                                                           |
| es_focus BooleanField(default=False)              | ✅ sí  | models.py:27                                                                           |
| areas_focus CharField(max_length=200, blank=True) | ✅ sí  | models.py:28-33                                                                        |
| es_aprobador_default BooleanField(default=False)  | ✅ sí  | models.py:34-37                                                                        |
| puede_aprobar BooleanField(default=False)         | ✅ sí  | models.py:38-41                                                                        |
| avatar_url URLField(blank=True)                   | ✅ sí  | models.py:42-46                                                                        |
| memoria_habilitada BooleanField(default=True)     | ✅ sí  | models.py:47-50                                                                        |
| USERNAME_FIELD = 'email'                          | ✅ sí  | models.py:52                                                                           |
| REQUIRED_FIELDS = ['first_name', 'last_name']     | ✅ sí  | models.py:53                                                                           |
| has_restricted_access() implementado              | ✅ sí  | models.py:73-74 — retorna True si perfil == Profile.USUARIO                            |
| can_access_restricted_content() implementado      | ✅ sí  | models.py:76-82 — retorna True para Administrador, Usuario IC, Heavy user, Macro       |
| indexes en perfil y es_focus                      | ✅ sí  | models.py:59-62 — Meta.indexes con ambos campos                                        |

### Requirements cubiertos

- **Req 3.1:** 5 perfiles definidos como choices ✅
- **Req 3.2:** campo perfil por usuario con constraint de choices ✅
- **Req 3.3:** campos persistibles en BD (se migrará en tarea 3.2) ✅
- **Req 8.1:** todos los campos del brief implementados ✅
- **Req 8.2:** email unique constraint declarado ✅
- **Req 8.5:** memoria_habilitada default=True ✅

### Fuera del alcance de esta tarea

- `settings.py` → AUTH_USER_MODEL (tarea 3.1)
- Migraciones (tarea 3.2)
- Modelo Role (tarea 2.3)
- Property tests (tarea 2.2)

---

## Veredicto

✅ **COMPLETED**

Todos los criterios de aceptación de la tarea 2.1 están implementados correctamente en `app/core/models.py`.

---

## Validación Kiro

### Criterios de tasks.md vs implementación

✅ email EmailField unique (USERNAME_FIELD) — línea 13
✅ perfil CharField con 5 Profile choices (TextChoices) — líneas 6-11
✅ roles ManyToManyField('Role', blank=True) — líneas 20-25
✅ cargo CharField(max_length=100, blank=True) — línea 26
✅ es_focus BooleanField(default=False) — línea 27
✅ areas_focus CharField(max_length=200, blank=True) — líneas 28-33
✅ es_aprobador_default BooleanField(default=False) — líneas 34-37
✅ puede_aprobar BooleanField(default=False) — líneas 38-41
✅ avatar_url URLField(blank=True) — líneas 42-46
✅ memoria_habilitada BooleanField(default=True) — líneas 47-50
✅ USERNAME_FIELD = 'email' — línea 52
✅ REQUIRED_FIELDS = ['first_name', 'last_name'] — línea 53
✅ has_restricted_access() implementado — líneas 73-74
✅ can_access_restricted_content() implementado — líneas 76-82
✅ indexes en perfil y es_focus en Meta — líneas 59-62
✅ Sintaxis verificada: python3 -m py_compile → OK (exit code 0)

### Validación contra requirements.md

**Requirement 3** (Perfiles):

- ✅ AC 3.1: Sistema soporta exactamente 5 perfiles
- ✅ AC 3.2: Asigna exactamente un perfil a cada usuario (CharField con choices)
- ✅ AC 3.3: Almacena perfil persistentemente (campo de modelo Django)

**Requirement 8** (Campos de usuario):

- ✅ AC 8.1: Almacena todos los campos requeridos
- ✅ AC 8.2: Email es unique
- ✅ AC 8.5: memoria_habilitada default=True

### Conclusión

La tarea 2.1 cumple **todos** los criterios de aceptación definidos en tasks.md y valida correctamente contra los requirements correspondientes (3.1-3.3, 8.1, 8.2, 8.5).

El código es sintácticamente correcto, está bien estructurado, sigue las convenciones de Django, y solo modifica el archivo especificado (app/core/models.py). Los métodos auxiliares has_restricted_access() y can_access_restricted_content() implementan correctamente la lógica de permisos según perfil.

**Estado:** Tarea marcada como [x] completed en tasks.md
**Progreso actualizado:** PROGRESO.md refleja tarea 2.1 completed, tarea 2.2 siguiente
