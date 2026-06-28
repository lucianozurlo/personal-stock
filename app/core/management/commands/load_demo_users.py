"""
Comando para cargar la base demo de 100 usuarios desde un fixture JSON o CSV.

Valida todas las reglas de negocio ANTES de cargar. Si hay errores, rechaza
la carga completa y reporta todos los errores encontrados.

Uso:
    python manage.py load_demo_users --fixture fixtures/demo_users.json
    python manage.py load_demo_users --fixture fixtures/demo_users.json --dry-run
    python manage.py load_demo_users --csv path/to/usuarios.csv
"""
import csv
import json
import os

from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Carga usuarios demo desde fixture JSON o CSV con validación completa'

    SPECIFIC_USERS = {
        'comustock.ci@gmail.com':   ('Luciano',   'Zurlo',             'Administrador'),
        'comustock.uci1@gmail.com': ('Diego',     'Ferrari',           'Usuario IC'),
        'comustock.uci2@gmail.com': ('Sara',      'Astudillo',         'Usuario IC'),
        'comustock.uci3@gmail.com': ('Martín',    'Caso',              'Usuario IC'),
        'comustock.uci4@gmail.com': ('Sebastián', 'Álvarez Hincaipié', 'Usuario IC'),
        'comustock.uci5@gmail.com': ('Emiliano',  'Zabuski',           'Usuario IC'),
        'comustock.g2@gmail.com':   ('Jonathan',  'Ferraro',           'Usuario IC'),
        'comustock.g1@gmail.com':   ('Luciana',   'Dau',               'Usuario IC'),
        'comustock.u1@gmail.com':   ('Pablo',     'Giglio',            'Usuario'),
        'comustock.u2@gmail.com':   ('Javier',    'Vulich',            'Usuario'),
        'comustock.u3@gmail.com':   ('Sebastián', 'Marzico',           'Usuario'),
        'comustock.u4@gmail.com':   ('Santiago',  'Gugger',            'Usuario'),
    }

    VALID_PROFILES = {'Administrador', 'Usuario IC', 'Heavy user', 'Macro', 'Usuario'}

    VALID_ROLES = {
        'Diseñador', 'Desarrollador', 'Redactor', 'Productor',
        'Gerente Cultura', 'Gerente IC', 'Especialista',
    }

    REQUIRED_FIELDS = ('first_name', 'last_name', 'email', 'perfil')

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--fixture', type=str, help='Ruta al archivo JSON fixture')
        group.add_argument('--csv', type=str, help='Ruta al archivo CSV')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Validar sin cargar datos en la base de datos',
        )

    def handle(self, *args, **options):
        fixture_path = options.get('fixture')
        csv_path = options.get('csv')
        dry_run = options['dry_run']

        if fixture_path:
            users, role_map, parse_errors = self._parse_fixture(fixture_path)
        else:
            users, role_map, parse_errors = self._parse_csv(csv_path)

        if parse_errors:
            for err in parse_errors:
                self.stderr.write(self.style.ERROR(err))
            raise CommandError('Carga rechazada por errores de parseo.')

        validation_errors = self._validate(users, role_map)
        if validation_errors:
            for err in validation_errors:
                self.stderr.write(self.style.ERROR(err))
            raise CommandError('Carga rechazada por errores de validación.')

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Validación exitosa (dry-run). {len(users)} usuarios listos para cargar. No se cargaron datos.'
                )
            )
            return

        if fixture_path:
            abs_path = self._resolve_path(fixture_path)
            call_command('loaddata', abs_path, verbosity=0)
        else:
            self._load_from_csv(users, role_map)

        self.stdout.write(
            self.style.SUCCESS(f'Carga exitosa: {len(users)} usuarios cargados.')
        )

    # ─── Parsers ─────────────────────────────────────────────────────────────

    def _parse_fixture(self, path):
        """Parsea fixture JSON de Django. Retorna (users, role_map, errors)."""
        abs_path = self._resolve_path(path)

        try:
            with open(abs_path, encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            return [], {}, [f'Error: Archivo no encontrado: {abs_path}']
        except json.JSONDecodeError as exc:
            return [], {}, [f'Error: JSON inválido en {abs_path}: {exc}']

        role_map = {}   # pk (int) → nombre (str)
        users = []

        for obj in data:
            model = obj.get('model', '')
            fields = obj.get('fields', {})

            if model == 'core.role':
                pk = obj.get('pk')
                name = fields.get('name', '')
                if pk is not None and name:
                    role_map[pk] = name

            elif model == 'core.user':
                users.append({
                    'first_name': fields.get('first_name', ''),
                    'last_name':  fields.get('last_name', ''),
                    'email':      fields.get('email', ''),
                    'perfil':     fields.get('perfil', ''),
                    'roles':      fields.get('roles', []),  # lista de PKs
                })

        return users, role_map, []

    def _parse_csv(self, path):
        """Parsea CSV con columnas estándar. Retorna (users, role_map, errors)."""
        abs_path = self._resolve_path(path)

        try:
            file = open(abs_path, encoding='utf-8', newline='')
        except FileNotFoundError:
            return [], {}, [f'Error: Archivo no encontrado: {abs_path}']

        # role_map identidad: nombre → nombre (CSV ya usa nombres, no PKs)
        role_map = {name: name for name in self.VALID_ROLES}
        users = []
        errors = []

        try:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader, start=2):  # fila 1 = header
                # Ignorar líneas de comentario (empieza con #)
                if row.get('first_name', '').startswith('#'):
                    continue
                roles_raw = row.get('roles', '')
                roles = [r.strip() for r in roles_raw.split(';') if r.strip()] if roles_raw else []

                users.append({
                    'first_name': row.get('first_name', '').strip(),
                    'last_name':  row.get('last_name', '').strip(),
                    'email':      row.get('email', '').strip(),
                    'perfil':     row.get('perfil', '').strip(),
                    'roles':      roles,
                    'cargo':      row.get('cargo', '').strip(),
                    'es_focus':   self._parse_bool(row.get('es_focus', '')),
                    'areas_focus': row.get('areas_focus', '').strip(),
                    'es_aprobador_default': self._parse_bool(row.get('es_aprobador_default', '')),
                    'puede_aprobar': self._parse_bool(row.get('puede_aprobar', '')),
                    'avatar_url': row.get('avatar_url', '').strip(),
                    'memoria_habilitada': self._parse_bool(row.get('memoria_habilitada', 'true')),
                })
        except Exception as exc:
            errors.append(f'Error leyendo CSV: {exc}')
        finally:
            file.close()

        return users, role_map, errors

    # ─── Validación ──────────────────────────────────────────────────────────

    def _validate(self, users, role_map):
        """Valida todas las reglas de negocio. Retorna lista de errores (puede ser vacía)."""
        errors = []

        # 1. Total de usuarios
        if len(users) != 100:
            errors.append(
                f'Error: Se esperaban 100 usuarios, se encontraron {len(users)}'
            )

        # Indexar por email para validaciones siguientes
        emails_seen = set()
        email_to_user = {}

        for user in users:
            email = user.get('email', '')

            # 2. Campos obligatorios
            for field in self.REQUIRED_FIELDS:
                if not user.get(field):
                    errors.append(
                        f'Error: Usuario {email or "sin email"} tiene campo obligatorio faltante: {field}'
                    )

            if not email:
                continue

            # 3. Emails únicos
            if email in emails_seen:
                errors.append(f'Error: Email duplicado: {email}')
            emails_seen.add(email)
            email_to_user[email] = user

            # 4. Perfil válido
            perfil = user.get('perfil', '')
            if perfil and perfil not in self.VALID_PROFILES:
                errors.append(f'Error: Perfil inválido en {email}: {perfil}')

            # 5 y 6. Roles según perfil
            roles = user.get('roles', [])
            if perfil == 'Usuario IC':
                for role_ref in roles:
                    role_name = role_map.get(role_ref, role_ref) if isinstance(role_ref, int) else role_ref
                    if role_name not in self.VALID_ROLES:
                        errors.append(f'Error: Rol inválido en {email}: {role_name}')
            else:
                if roles:
                    errors.append(
                        f'Error: Usuario {email} con perfil {perfil} tiene roles asignados '
                        f'(solo permitido para Usuario IC)'
                    )

        # 7. Los 12 usuarios específicos deben estar presentes con datos correctos
        for spec_email, (first_name, last_name, perfil) in self.SPECIFIC_USERS.items():
            if spec_email not in email_to_user:
                errors.append(
                    f'Error: Falta usuario específico: {spec_email}. '
                    f'Se requieren los 12 usuarios definidos en requirements.md'
                )
            else:
                user = email_to_user[spec_email]
                if user.get('perfil') != perfil:
                    errors.append(
                        f'Error: Usuario {spec_email} tiene perfil {user.get("perfil")}, '
                        f'se esperaba {perfil}'
                    )

        return errors

    # ─── Carga desde CSV vía ORM ─────────────────────────────────────────────

    def _load_from_csv(self, users, role_map):
        """Crea o actualiza usuarios desde datos CSV usando el ORM de Django."""
        from django.contrib.auth import get_user_model
        from core.models import Role

        User = get_user_model()

        # Asegurar que existen los roles
        for role_name in self.VALID_ROLES:
            Role.objects.get_or_create(name=role_name)

        for user_data in users:
            email = user_data['email']
            defaults = {
                'first_name':          user_data['first_name'],
                'last_name':           user_data['last_name'],
                'username':            email,
                'perfil':              user_data['perfil'],
                'cargo':               user_data.get('cargo', ''),
                'es_focus':            user_data.get('es_focus', False),
                'areas_focus':         user_data.get('areas_focus', ''),
                'es_aprobador_default': user_data.get('es_aprobador_default', False),
                'puede_aprobar':       user_data.get('puede_aprobar', False),
                'avatar_url':          user_data.get('avatar_url', ''),
                'memoria_habilitada':  user_data.get('memoria_habilitada', True),
                'is_active':           True,
            }

            user_obj, _ = User.objects.update_or_create(email=email, defaults=defaults)

            if not user_obj.password or user_obj.password == '':
                user_obj.password = make_password('demo1234')
                user_obj.save()

            # Asignar roles
            role_names = user_data.get('roles', [])
            if role_names:
                role_objs = Role.objects.filter(name__in=role_names)
                user_obj.roles.set(role_objs)
            else:
                user_obj.roles.clear()

    # ─── Utilidades ──────────────────────────────────────────────────────────

    def _resolve_path(self, path):
        """Resuelve path relativo desde el CWD (directorio app/)."""
        if os.path.isabs(path):
            return path
        return os.path.abspath(path)

    @staticmethod
    def _parse_bool(value):
        return str(value).strip().lower() in ('true', '1', 'yes', 'si', 'sí')
