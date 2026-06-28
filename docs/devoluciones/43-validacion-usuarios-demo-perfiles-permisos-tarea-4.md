# Validación — Tarea 4: Checkpoint Migración de User Model

**Spec:** usuarios-demo-perfiles-permisos
**Tarea:** 4 — Checkpoint: Validar migración de User Model
**Fecha:** 2026-06-22
**Veredicto:** ✅ COMPLETED — Validado por Kiro

---

## Qué se validó

Checkpoint de verificación post-migración a AbstractUser. No se agrega código nuevo de dominio; se verifica que la migración aplicada en tareas 1.1–3.3 es correcta y el sistema es funcional.

---

## Comandos ejecutados

```bash
# 1. System check
cd app && python manage.py check
# → System check identified no issues (0 silenced)

# 2. Introspección de tablas y campos
python manage.py shell -c "
from django.db import connection
tables = connection.introspection.table_names()
# (filtrado por 'core' y 'auth')
..."

# 3. Tests completos
python -Wa manage.py test core --verbosity=2
# → Ran 12 tests in 391.061s — OK
```

---

## Hallazgos por criterio

### Criterio 1: Superusuario puede autenticarse correctamente

**Estado: SÍ**

- Shell: `User.objects.filter(email='test@personal.com.ar').first()` → Existe: True, Perfil: Administrador, is_superuser: True, is_staff: True
- Test `AuthViewsTest.test_login_view_post_valid`: OK — POST a `/login/` con email+password redirige a `/` con status 200
- Test `AuthViewsTest.test_home_view_authenticated`: OK — `client.login()` funciona y home responde 200

---

### Criterio 2: Tabla core_user existe con todos los campos

**Estado: SÍ**

Campos confirmados por introspección:

| Campo                | Origen                          |
| -------------------- | ------------------------------- |
| id                   | AbstractUser                    |
| password             | AbstractUser                    |
| last_login           | AbstractUser                    |
| is_superuser         | AbstractUser                    |
| username             | AbstractUser                    |
| first_name           | AbstractUser                    |
| last_name            | AbstractUser                    |
| is_staff             | AbstractUser                    |
| is_active            | AbstractUser                    |
| date_joined          | AbstractUser                    |
| email                | custom (unique, USERNAME_FIELD) |
| perfil               | custom (choices 5 perfiles)     |
| cargo                | custom                          |
| es_focus             | custom                          |
| areas_focus          | custom                          |
| es_aprobador_default | custom                          |
| puede_aprobar        | custom                          |
| avatar_url           | custom                          |
| memoria_habilitada   | custom                          |

Total: 19 campos. Coinciden exactamente con `core/models.py`.

---

### Criterio 3: Tabla core_role existe

**Estado: SÍ**

`core_role` aparece en `connection.introspection.table_names()`. Tabla creada por `0001_initial.py`.

---

### Criterio 4: Tabla intermedia core_user_roles existe

**Estado: SÍ**

`core_user_roles` aparece en la introspección. Es la tabla ManyToMany entre `core_user` y `core_role`.

Otras tablas relacionales también presentes: `core_user_groups`, `core_user_user_permissions` (heredadas de AbstractUser).

---

### Criterio 5: Reportar resultados punto por punto

**Estado: SÍ** — este documento.

---

## Suite de tests: 12/12 OK

```
test_home_view_authenticated         ... ok
test_home_view_unauthenticated       ... ok
test_login_view_get                  ... ok
test_login_view_post_invalid         ... ok
test_login_view_post_valid           ... ok
test_logout_view                     ... ok
test_static_files_configuration      ... ok
test_template_configuration          ... ok
test_property_3_role_assignment_usuario_ic  ... ok
test_property_4_role_restriction_non_usuario_ic ... ok
test_property_1_email_uniqueness     ... ok
test_property_2_profile_persistence  ... ok

Ran 12 tests in 391.061s — OK
```

---

## Cambio adicional — Bug fixes en tests.py

Durante la ejecución del checkpoint se detectaron 2 bugs preexistentes en `tests.py`. Se corrigieron en la misma sesión según protocolo.

### Bug 1: AuthViewsTest usaba auth.User en lugar de get_user_model()

**Síntoma:** `AttributeError: Manager isn't available; 'auth.User' has been swapped for 'core.User'` — 6 tests en ERROR.

**Causa:** Línea 2 importaba `from django.contrib.auth.models import User`. Con `AUTH_USER_MODEL = 'core.User'`, el manager de `auth.User` queda inaccesible (swapped out).

**Fix aplicado:**

- `tests.py` línea 2: `from django.contrib.auth.models import User` → `from django.contrib.auth import get_user_model`
- `tests.py` línea 34 (setUp): agregado `User = get_user_model()` antes de `create_user()`

### Bug 2: Hypothesis deadline=1000ms insuficiente para tests con DB

**Síntoma:** `hypothesis.errors.DeadlineExceeded: Test took 1546.70ms, which exceeds the deadline of 1000.00ms` — Property 1 en ERROR.

**Causa:** `hyp_settings.register_profile("usuarios", ..., deadline=1000)` — 1 segundo es insuficiente para operaciones de base de datos en la primera iteración de Hypothesis.

**Fix aplicado:**

- `tests.py` línea 14: `deadline=1000` → `deadline=None` (deshabilita enforcement de deadline para tests con DB, que es la práctica recomendada por Hypothesis).

---

## Diff resumen

**Archivo modificado:** `app/core/tests.py`

- Línea 2: `from django.contrib.auth.models import User` → `from django.contrib.auth import get_user_model`
- Línea 14: `deadline=1000` → `deadline=None`
- Línea 34 (setUp): +`User = get_user_model()` antes de `create_user()`

---

## Validación Final por Kiro

**Fecha validación:** 2026-06-22

### Comprobaciones realizadas

1. ✅ **Django check:** `python manage.py check` — System check identified no issues (0 silenced)
2. ✅ **Suite de tests:** Ran 12 tests in 372.229s — OK
3. ✅ **Instalación de hypothesis:** Se detectó que hypothesis estaba en requirements.txt pero no instalado. Se instaló exitosamente y los tests pasaron.

### Criterios de aceptación validados

| Criterio                                      | Estado | Validación Kiro                                                                    |
| --------------------------------------------- | ------ | ---------------------------------------------------------------------------------- |
| Superusuario puede autenticarse correctamente | ✅     | Confirmado por tests `test_login_view_post_valid` y `test_home_view_authenticated` |
| Tabla core_user existe con todos los campos   | ✅     | Confirmado por introspección reportada + migración 0001_initial aplicada           |
| Tabla core_role existe                        | ✅     | Confirmado por introspección reportada                                             |
| Tabla core_user_roles existe                  | ✅     | Confirmado por introspección reportada (ManyToMany intermedia)                     |
| Reportar resultados punto por punto           | ✅     | Este documento                                                                     |

### Análisis de los bug fixes

Los 2 bugs corregidos por Claude Code durante el checkpoint son **legítimos y apropiados**:

1. **Bug 1 (auth.User swapped):** Correcto. Con `AUTH_USER_MODEL = 'core.User'`, el modelo `auth.User` queda swapped out y no se debe referenciar directamente. El fix con `get_user_model()` es la práctica recomendada por Django.

2. **Bug 2 (Hypothesis deadline):** Correcto. `deadline=None` es la configuración recomendada por Hypothesis para tests que involucran DB, ya que las operaciones de I/O pueden ser lentas en la primera iteración.

### Decisión

**TAREA 4 COMPLETED** — Todos los criterios de aceptación se cumplen:

- La migración a AbstractUser fue exitosa
- El superusuario se preservó correctamente
- Las 3 tablas core (core_user, core_role, core_user_roles) existen
- Los 12 tests pasan sin errores
- Los bug fixes aplicados son correctos y necesarios

### Próximos pasos

Continuar con tarea 5.1: Crear clase DatasetFilter en `app/core/permissions.py`.
