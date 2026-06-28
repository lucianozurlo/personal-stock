import json
import os
import tempfile
from io import StringIO

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
from django.core.management import call_command
from django.core.management.base import CommandError

# ─── Property-based tests: usuarios-demo-perfiles-permisos ───────────────────
from hypothesis import given, settings as hyp_settings
from hypothesis import strategies as st
from hypothesis.extra.django import TestCase as HypothesisTestCase

from core.models import User as CoreUser, Role  # Requiere AUTH_USER_MODEL + migración (tareas 3.1, 3.2)
from core.permissions import DatasetFilter
from core.management.commands.load_demo_users import Command as LoadDemoUsersCommand
from core.serializers.chat_serializers import (
    RequestPayloadSerializer,
    ResponsePayloadSerializer,
)

hyp_settings.register_profile("usuarios", max_examples=100, deadline=None)
hyp_settings.load_profile("usuarios")

perfil_valido = st.sampled_from([
    'Administrador', 'Usuario IC', 'Heavy user', 'Macro', 'Usuario'
])

rol_valido = st.sampled_from([
    'Diseñador', 'Desarrollador', 'Redactor', 'Productor',
    'Gerente Cultura', 'Gerente IC', 'Especialista'
])

perfil_no_ic = st.sampled_from([
    'Administrador', 'Heavy user', 'Macro', 'Usuario'
])


class AuthViewsTest(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='test@personal.com.ar',
            email='test@personal.com.ar',
            password='testpass123',
            first_name='Test',
            last_name='User',
        )

    def test_login_view_get(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_view_post_valid(self):
        response = self.client.post('/login/', {
            'email': 'test@personal.com.ar',
            'password': 'testpass123',
        })
        self.assertRedirects(response, '/')
        home = self.client.get('/')
        self.assertEqual(home.status_code, 200)

    def test_login_view_post_invalid(self):
        response = self.client.post('/login/', {
            'email': 'wrong@personal.com.ar',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)

    def test_home_view_authenticated(self):
        self.client.login(username='test@personal.com.ar', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertIn('user', response.context)
        self.assertIn('ps_user_data', response.context)

    def test_home_view_unauthenticated(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login/?next=/', fetch_redirect_response=False)

    def test_logout_view(self):
        self.client.login(username='test@personal.com.ar', password='testpass123')
        response = self.client.get('/logout/')
        self.assertRedirects(response, '/login/', fetch_redirect_response=False)
        home = self.client.get('/')
        self.assertEqual(home.status_code, 302)


class ConfigurationTest(TestCase):

    def test_static_files_configuration(self):
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'STATICFILES_DIRS'))
        self.assertTrue(len(settings.STATICFILES_DIRS) > 0)
        self.assertIsNotNone(finders.find('css/styles.css'))
        self.assertIsNotNone(finders.find('js/app.js'))
        self.assertIsNotNone(finders.find('img/personal-stock-logo.svg'))

    def test_template_configuration(self):
        from django.conf import settings
        expected_path = settings.BASE_DIR.parent / 'templates'
        self.assertIn(expected_path, settings.TEMPLATES[0]['DIRS'])
        try:
            get_template('login.html')
            login_found = True
        except TemplateDoesNotExist:
            login_found = False
        try:
            get_template('home.html')
            home_found = True
        except TemplateDoesNotExist:
            home_found = False
        self.assertTrue(login_found, "login.html debe ser encontrable por Django")
        self.assertTrue(home_found, "home.html debe ser encontrable por Django")


class UserPropertyTest(HypothesisTestCase):
    """
    Property-based tests para User model.
    Valida: Property 1 (Email Uniqueness) y Property 2 (Profile Persistence).
    Requiere: Role model (tarea 2.3) + AUTH_USER_MODEL (tarea 3.1) + migrations (tarea 3.2).
    """

    @given(email=st.emails())
    def test_property_1_email_uniqueness(self, email):
        """
        Feature: usuarios-demo-perfiles-permisos, Property 1: Email Uniqueness
        Para cualquier conjunto de usuarios creados, todos los emails deben ser únicos.
        Validates: Requirements 1.6, 8.2
        """
        CoreUser.objects.create_user(
            username=email,
            email=email,
            first_name='Test',
            last_name='User',
            password='testpass123',
        )
        with self.assertRaises(Exception):
            CoreUser.objects.create_user(
                username=email + '_dup',
                email=email,
                first_name='Duplicado',
                last_name='User',
                password='testpass123',
            )

    @given(
        perfil=perfil_valido,
        email=st.emails(),
    )
    def test_property_2_profile_persistence(self, perfil, email):
        """
        Feature: usuarios-demo-perfiles-permisos, Property 2: Profile Assignment Persistence
        Para cualquier usuario con perfil válido, al guardarlo y recargarlo, el perfil persiste.
        Validates: Requirements 3.2, 3.3
        """
        user = CoreUser.objects.create_user(
            username=email,
            email=email,
            first_name='Test',
            last_name='User',
            password='testpass123',
            perfil=perfil,
        )
        reloaded = CoreUser.objects.get(pk=user.pk)
        self.assertEqual(reloaded.perfil, perfil)


class RolePropertyTest(HypothesisTestCase):
    """
    Property-based tests para Role assignment.
    Valida: Property 3 (Role Assignment for Usuario IC)
            Property 4 (Role Restriction for Non-Usuario IC).
    Requiere: Role model (tarea 2.3) + AUTH_USER_MODEL (tarea 3.1) + migrations (tarea 3.2).
    """

    @given(
        email=st.emails(),
        role_names=st.lists(
            st.sampled_from([
                'Diseñador', 'Desarrollador', 'Redactor', 'Productor',
                'Gerente Cultura', 'Gerente IC', 'Especialista'
            ]),
            min_size=0, max_size=7, unique=True,
        ),
    )
    def test_property_3_role_assignment_usuario_ic(self, email, role_names):
        """
        Feature: usuarios-demo-perfiles-permisos, Property 3: Role Assignment for Usuario IC
        Para cualquier usuario con perfil Usuario IC, se pueden asignar cero o más
        roles válidos del conjunto de 7, y todos persisten al recargar desde DB.
        Validates: Requirements 4.1, 4.3, 4.4
        """
        user = CoreUser.objects.create_user(
            username=email,
            email=email,
            first_name='Test',
            last_name='IC',
            password='testpass123',
            perfil='Usuario IC',
        )
        roles = []
        for name in role_names:
            role, _ = Role.objects.get_or_create(name=name)
            roles.append(role)
        user.roles.set(roles)

        reloaded = CoreUser.objects.get(pk=user.pk)
        assigned_names = set(reloaded.roles.values_list('name', flat=True))
        self.assertEqual(assigned_names, set(role_names))

    @given(
        email=st.emails(),
        perfil=st.sampled_from(['Administrador', 'Heavy user', 'Macro', 'Usuario']),
    )
    def test_property_4_role_restriction_non_usuario_ic(self, email, perfil):
        """
        Feature: usuarios-demo-perfiles-permisos, Property 4: Role Restriction for Non-Usuario IC
        Para cualquier usuario con perfil distinto de Usuario IC, roles.count() == 0.
        Validates: Requirements 4.2
        """
        user = CoreUser.objects.create_user(
            username=email,
            email=email,
            first_name='Test',
            last_name='NonIC',
            password='testpass123',
            perfil=perfil,
        )
        self.assertEqual(user.roles.count(), 0)
        reloaded = CoreUser.objects.get(pk=user.pk)
        self.assertEqual(reloaded.roles.count(), 0)


class DatasetFilterPropertyTest(HypothesisTestCase):
    """
    Property-based tests para DatasetFilter.
    Valida: Property 5 (Dataset Filtering by Restricted Substrings)
            Property 6 (Dataset Access for Privileged Profiles).
    Requiere: permissions.py (tarea 5.1) + User model (tarea 2.1).
    """

    _restricted_sub = st.sampled_from([
        'macro', 'MACRO', 'Macro',
        'macroestructura', 'MACROESTRUCTURA', 'Macroestructura',
        'líderes', 'LÍDERES', 'Líderes',
        'lideres', 'LIDERES', 'Lideres',
    ])

    _restricted_destinatario = st.builds(
        lambda sub: sub,
        sub=_restricted_sub,
    )

    @given(
        email=st.emails(),
        destinatario=_restricted_destinatario,
    )
    def test_property_5_filtering_restricted_substrings(self, email, destinatario):
        """
        Feature: usuarios-demo-perfiles-permisos, Property 5: Dataset Filtering by Restricted Substrings
        Para cualquier registro con destinatario que contenga substring restringida
        y usuario con perfil Usuario, filter_by_profile debe excluir ese registro.
        Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
        """
        user = CoreUser.objects.create_user(
            username=email,
            email=email,
            first_name='Test',
            last_name='Usuario',
            password='testpass123',
            perfil='Usuario',
        )
        record = {'destinatario': destinatario, 'asunto': 'Test'}
        result = DatasetFilter.filter_by_profile(user, [record])
        self.assertEqual(result, [])

    @given(
        email=st.emails(),
        destinatario=_restricted_destinatario,
        perfil=st.sampled_from(['Administrador', 'Usuario IC', 'Heavy user', 'Macro']),
    )
    def test_property_6_access_privileged_profiles(self, email, destinatario, perfil):
        """
        Feature: usuarios-demo-perfiles-permisos, Property 6: Dataset Access for Privileged Profiles
        Para cualquier registro con destinatario restringido y usuario con perfil privilegiado,
        filter_by_profile debe incluir ese registro (sin restricciones de destinatario).
        Validates: Requirements 5.7
        """
        user = CoreUser.objects.create_user(
            username=email,
            email=email,
            first_name='Test',
            last_name='Privileged',
            password='testpass123',
            perfil=perfil,
        )
        record = {'destinatario': destinatario, 'asunto': 'Test'}
        result = DatasetFilter.filter_by_profile(user, [record])
        self.assertIn(record, result)


class DatasetFilterUnitTest(TestCase):
    """
    Unit tests para DatasetFilter — casos borde deterministas.
    Valida: Requirement 5.5 (case-insensitive), Requirement 10.1 (ValueError sin perfil).
    """

    def setUp(self):
        self.usuario = CoreUser.objects.create_user(
            username='edge@test.com',
            email='edge@test.com',
            first_name='Edge',
            last_name='Case',
            password='testpass123',
            perfil='Usuario',
        )

    def test_user_none_raises_value_error(self):
        """user=None → ValueError (Req 10.1)"""
        with self.assertRaises(ValueError):
            DatasetFilter.filter_by_profile(None, [])

    def test_user_empty_perfil_raises_value_error(self):
        """user con perfil='' → ValueError (Req 10.1)"""
        class MockUser:
            perfil = ''
        with self.assertRaises(ValueError):
            DatasetFilter.filter_by_profile(MockUser(), [])

    def test_empty_dataset_returns_empty_list(self):
        """dataset vacío → lista vacía (Req 5.5)"""
        result = DatasetFilter.filter_by_profile(self.usuario, [])
        self.assertEqual(result, [])

    def test_destinatario_none_includes_record(self):
        """destinatario=None → incluir registro (Req 5.5)"""
        record = {'destinatario': None, 'asunto': 'Test'}
        result = DatasetFilter.filter_by_profile(self.usuario, [record])
        self.assertIn(record, result)

    def test_destinatario_empty_includes_record(self):
        """destinatario='' → incluir registro (Req 5.5)"""
        record = {'destinatario': '', 'asunto': 'Test'}
        result = DatasetFilter.filter_by_profile(self.usuario, [record])
        self.assertIn(record, result)

    def test_destinatario_missing_includes_record(self):
        """sin campo destinatario → incluir registro (Req 5.5)"""
        record = {'asunto': 'Sin destinatario'}
        result = DatasetFilter.filter_by_profile(self.usuario, [record])
        self.assertIn(record, result)

    def test_case_insensitive_macro_uppercase(self):
        """MACRO (mayúsculas) → excluido para perfil Usuario (Req 5.5)"""
        record = {'destinatario': 'MACRO', 'asunto': 'Test'}
        result = DatasetFilter.filter_by_profile(self.usuario, [record])
        self.assertEqual(result, [])

    def test_case_insensitive_macro_mixed(self):
        """Macro (mixto) → excluido para perfil Usuario (Req 5.5)"""
        record = {'destinatario': 'Macro', 'asunto': 'Test'}
        result = DatasetFilter.filter_by_profile(self.usuario, [record])
        self.assertEqual(result, [])

    def test_case_insensitive_macro_lowercase(self):
        """macro (minúsculas) → excluido para perfil Usuario (Req 5.5)"""
        record = {'destinatario': 'macro', 'asunto': 'Test'}
        result = DatasetFilter.filter_by_profile(self.usuario, [record])
        self.assertEqual(result, [])

    def test_is_record_restricted_privileged_user_returns_false(self):
        """is_record_restricted: usuario privilegiado → False aunque destinatario sea restringido"""
        admin = CoreUser.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            first_name='Admin',
            last_name='Test',
            password='testpass123',
            perfil='Administrador',
        )
        record = {'destinatario': 'macro y lideres', 'asunto': 'Restringido'}
        self.assertFalse(DatasetFilter.is_record_restricted(record, admin))

    def test_is_record_restricted_usuario_restricted_record_returns_true(self):
        """is_record_restricted: perfil Usuario + destinatario restringido → True"""
        record = {'destinatario': 'LÍDERES de área', 'asunto': 'Restringido'}
        self.assertTrue(DatasetFilter.is_record_restricted(record, self.usuario))

    def test_is_record_restricted_usuario_allowed_record_returns_false(self):
        """is_record_restricted: perfil Usuario + destinatario no restringido → False"""
        record = {'destinatario': 'FULL COMPAÑÍA', 'asunto': 'Libre'}
        self.assertFalse(DatasetFilter.is_record_restricted(record, self.usuario))


class DatasetFilterPerformanceTest(TestCase):
    """
    Performance test para DatasetFilter con dataset real.
    Valida: Requirement 10.3 — filtro ejecuta en <50ms con dataset completo.
    """

    def setUp(self):
        self.usuario = CoreUser.objects.create_user(
            username='perf@test.com',
            email='perf@test.com',
            first_name='Perf',
            last_name='Test',
            password='testpass123',
            perfil='Usuario',
        )

    def test_performance_filter_under_50ms(self):
        """
        Integration/Performance: DatasetFilter ejecuta en <50ms con dataset real.
        Validates: Requirement 10.3
        """
        import json
        import time
        from django.conf import settings

        dataset_path = settings.BASE_DIR.parent / 'mails' / 'output' / 'relevamiento_enriquecido.json'

        if not dataset_path.exists():
            self.skipTest(f"Dataset no encontrado en {dataset_path}")

        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)

        start = time.perf_counter()
        filtered = DatasetFilter.filter_by_profile(self.usuario, dataset)
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000
        self.assertLess(
            elapsed_ms, 50,
            f"Filtro tomó {elapsed_ms:.2f}ms, límite es 50ms"
        )
        self.assertIsInstance(filtered, list)


class FixtureValidationTest(TestCase):
    """
    Unit tests que validan el fixture demo_users.json contra los criterios del spec.
    Validates: Requirements 1.1, 1.3, 1.4, 1.6, 2.1-2.12, 4.2
    """
    fixtures = ['demo_users.json']

    SPECIFIC_USERS = [
        ('comustock.ci@gmail.com',   'Luciano',   'Zurlo',             'Administrador'),
        ('comustock.uci1@gmail.com', 'Diego',     'Ferrari',           'Usuario IC'),
        ('comustock.uci2@gmail.com', 'Sara',      'Astudillo',         'Usuario IC'),
        ('comustock.uci3@gmail.com', 'Martín',    'Caso',              'Usuario IC'),
        ('comustock.uci4@gmail.com', 'Sebastián', 'Álvarez Hincaipié', 'Usuario IC'),
        ('comustock.uci5@gmail.com', 'Emiliano',  'Zabuski',           'Usuario IC'),
        ('comustock.g2@gmail.com',   'Jonathan',  'Ferraro',           'Usuario IC'),
        ('comustock.g1@gmail.com',   'Luciana',   'Dau',               'Usuario IC'),
        ('comustock.u1@gmail.com',   'Pablo',     'Giglio',            'Usuario'),
        ('comustock.u2@gmail.com',   'Javier',    'Vulich',            'Usuario'),
        ('comustock.u3@gmail.com',   'Sebastián', 'Marzico',           'Usuario'),
        ('comustock.u4@gmail.com',   'Santiago',  'Gugger',            'Usuario'),
    ]

    def test_total_users_100(self):
        """Req 1.1: exactamente 100 usuarios en la base demo."""
        self.assertEqual(CoreUser.objects.count(), 100)

    def test_12_specific_users_present(self):
        """Req 2.1-2.12: los 12 usuarios específicos existen con datos correctos."""
        for email, first_name, last_name, perfil in self.SPECIFIC_USERS:
            with self.subTest(email=email):
                user = CoreUser.objects.get(email=email)
                self.assertEqual(user.first_name, first_name)
                self.assertEqual(user.last_name, last_name)
                self.assertEqual(user.perfil, perfil)

    def test_profile_distribution_minimum(self):
        """Req 1.3, 1.4: al menos 15 Usuario IC y 30 Usuario."""
        self.assertGreaterEqual(CoreUser.objects.filter(perfil='Usuario IC').count(), 15)
        self.assertGreaterEqual(CoreUser.objects.filter(perfil='Usuario').count(), 30)

    def test_emails_unique(self):
        """Req 1.6, 8.2: ningún email duplicado en la base demo."""
        total = CoreUser.objects.count()
        unique = CoreUser.objects.values('email').distinct().count()
        self.assertEqual(total, unique)

    def test_roles_only_for_usuario_ic(self):
        """Req 4.2: usuarios sin perfil Usuario IC no tienen roles asignados."""
        non_ic_with_roles = (
            CoreUser.objects.exclude(perfil='Usuario IC')
            .filter(roles__isnull=False)
            .distinct()
        )
        self.assertEqual(
            non_ic_with_roles.count(), 0,
            f"Usuarios no-IC con roles: {list(non_ic_with_roles.values_list('email', flat=True))}"
        )

    def test_all_7_roles_assigned_at_least_once(self):
        """Req 4.1: cada uno de los 7 roles está asignado al menos a un usuario."""
        role_names = [
            'Diseñador', 'Desarrollador', 'Redactor', 'Productor',
            'Gerente Cultura', 'Gerente IC', 'Especialista',
        ]
        for name in role_names:
            with self.subTest(role=name):
                count = CoreUser.objects.filter(roles__name=name).count()
                self.assertGreater(count, 0, f"Ningún usuario tiene el rol '{name}'")


class LoadDemoUsersPropertyTest(HypothesisTestCase):
    """
    Property-based tests para la validación del comando load_demo_users.
    Valida: Property 7 (Profile Validation), Property 8 (Invalid Role Assignment Rejection),
            Property 9 (CSV Load Rejection on Missing Fields).
    Requiere: load_demo_users.py (tarea 8.1).
    """

    _VALID_PROFILES = {'Administrador', 'Usuario IC', 'Heavy user', 'Macro', 'Usuario'}
    _VALID_ROLES = {
        'Diseñador', 'Desarrollador', 'Redactor', 'Productor',
        'Gerente Cultura', 'Gerente IC', 'Especialista',
    }

    @given(
        email=st.emails(),
        invalid_perfil=st.text(min_size=1).filter(
            lambda p: p.strip() not in {
                'Administrador', 'Usuario IC', 'Heavy user', 'Macro', 'Usuario'
            }
        ),
    )
    def test_property_7_profile_validation(self, email, invalid_perfil):
        """
        Feature: usuarios-demo-perfiles-permisos, Property 7: Profile Validation
        Para cualquier perfil inválido, _validate() debe reportar error 'Perfil inválido'.
        Validates: Requirement 8.3
        """
        cmd = LoadDemoUsersCommand()
        role_map = {n: n for n in LoadDemoUsersCommand.VALID_ROLES}
        users = [{
            'first_name': 'Test',
            'last_name': 'User',
            'email': email,
            'perfil': invalid_perfil,
            'roles': [],
        }]
        errors = cmd._validate(users, role_map)
        perfil_errors = [e for e in errors if 'Perfil inválido' in e]
        self.assertTrue(
            len(perfil_errors) > 0,
            f"Se esperaba error 'Perfil inválido' para perfil={invalid_perfil!r}, "
            f"pero errors={errors}",
        )

    @given(
        email=st.emails(),
        invalid_role=st.text(min_size=1).filter(
            lambda r: r.strip() not in {
                'Diseñador', 'Desarrollador', 'Redactor', 'Productor',
                'Gerente Cultura', 'Gerente IC', 'Especialista',
            }
        ),
    )
    def test_property_8_invalid_role_rejection(self, email, invalid_role):
        """
        Feature: usuarios-demo-perfiles-permisos, Property 8: Invalid Role Assignment Rejection
        Para cualquier rol inválido asignado a un Usuario IC, _validate() debe reportar
        error 'Rol inválido'.
        Validates: Requirement 8.4
        """
        cmd = LoadDemoUsersCommand()
        role_map = {n: n for n in LoadDemoUsersCommand.VALID_ROLES}
        role_name = invalid_role.strip() or '\x00'  # garantizar no-vacío post-strip
        users = [{
            'first_name': 'Test',
            'last_name': 'User',
            'email': email,
            'perfil': 'Usuario IC',
            'roles': [role_name],
        }]
        errors = cmd._validate(users, role_map)
        role_errors = [e for e in errors if 'Rol inválido' in e]
        self.assertTrue(
            len(role_errors) > 0,
            f"Se esperaba error 'Rol inválido' para rol={role_name!r}, "
            f"pero errors={errors}",
        )

    @given(
        email=st.emails(),
        missing_field=st.sampled_from(['first_name', 'last_name', 'email', 'perfil']),
    )
    def test_property_9_csv_rejection_missing_fields(self, email, missing_field):
        """
        Feature: usuarios-demo-perfiles-permisos, Property 9: CSV Load Rejection on Missing Fields
        Para cualquier campo obligatorio vacío (first_name, last_name, email, perfil),
        _validate() debe reportar error 'campo obligatorio faltante'.
        Validates: Requirement 7.5
        """
        cmd = LoadDemoUsersCommand()
        role_map = {n: n for n in LoadDemoUsersCommand.VALID_ROLES}
        user = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': email,
            'perfil': 'Usuario',
            'roles': [],
        }
        user[missing_field] = ''  # vaciar el campo obligatorio
        errors = cmd._validate([user], role_map)
        field_errors = [e for e in errors if 'campo obligatorio faltante' in e]
        self.assertTrue(
            len(field_errors) > 0,
            f"Se esperaba error 'campo obligatorio faltante' para campo={missing_field!r}, "
            f"pero errors={errors}",
        )


class LoadDemoUsersIntegrationTest(TestCase):
    """
    Integration tests para el comando load_demo_users end-to-end.
    Valida carga desde fixture, dry-run, y rechazo por errores de validación.
    Requiere: load_demo_users.py (tarea 8.1), demo_users.json (tarea 7.1).
    Validates: Requirements 7.2, 7.3, 7.4, 7.6
    """

    FIXTURE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'fixtures', 'demo_users.json'
    )

    SPECIFIC_USERS = [
        ('comustock.ci@gmail.com',   'Luciano',   'Zurlo',             'Administrador'),
        ('comustock.uci1@gmail.com', 'Diego',     'Ferrari',           'Usuario IC'),
        ('comustock.uci2@gmail.com', 'Sara',      'Astudillo',         'Usuario IC'),
        ('comustock.uci3@gmail.com', 'Martín',    'Caso',              'Usuario IC'),
        ('comustock.uci4@gmail.com', 'Sebastián', 'Álvarez Hincaipié', 'Usuario IC'),
        ('comustock.uci5@gmail.com', 'Emiliano',  'Zabuski',           'Usuario IC'),
        ('comustock.g2@gmail.com',   'Jonathan',  'Ferraro',           'Usuario IC'),
        ('comustock.g1@gmail.com',   'Luciana',   'Dau',               'Usuario IC'),
        ('comustock.u1@gmail.com',   'Pablo',     'Giglio',            'Usuario'),
        ('comustock.u2@gmail.com',   'Javier',    'Vulich',            'Usuario'),
        ('comustock.u3@gmail.com',   'Sebastián', 'Marzico',           'Usuario'),
        ('comustock.u4@gmail.com',   'Santiago',  'Gugger',            'Usuario'),
    ]

    def test_load_from_fixture_creates_100_users(self):
        """Test carga exitosa desde fixture demo_users.json — Requirement 7.2."""
        call_command('load_demo_users', fixture=self.FIXTURE_PATH,
                     stdout=StringIO(), stderr=StringIO())
        self.assertEqual(CoreUser.objects.count(), 100)

    def test_12_specific_users_present_after_load(self):
        """Test validación de 12 usuarios específicos después de carga — Requirement 7.3."""
        call_command('load_demo_users', fixture=self.FIXTURE_PATH,
                     stdout=StringIO(), stderr=StringIO())
        for email, first_name, last_name, perfil in self.SPECIFIC_USERS:
            with self.subTest(email=email):
                user = CoreUser.objects.get(email=email)
                self.assertEqual(user.first_name, first_name)
                self.assertEqual(user.last_name, last_name)
                self.assertEqual(user.perfil, perfil)

    def test_dry_run_does_not_create_users(self):
        """Test dry-run no crea usuarios en la base de datos — Requirement 7.4."""
        call_command('load_demo_users', fixture=self.FIXTURE_PATH,
                     dry_run=True, stdout=StringIO(), stderr=StringIO())
        self.assertEqual(CoreUser.objects.count(), 0)

    def test_reject_fixture_with_missing_required_user(self):
        """Test rechazo de fixture con usuario específico faltante — Requirement 7.6."""
        with open(self.FIXTURE_PATH, encoding='utf-8') as f:
            fixture_data = json.load(f)

        # Eliminar a Luciano Zurlo (comustock.ci@gmail.com)
        modified = [
            entry for entry in fixture_data
            if not (
                entry.get('model') == 'core.user'
                and entry.get('fields', {}).get('email') == 'comustock.ci@gmail.com'
            )
        ]

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False, encoding='utf-8'
        ) as tmp:
            json.dump(modified, tmp, ensure_ascii=False)
            temp_path = tmp.name

        try:
            with self.assertRaises(CommandError):
                call_command('load_demo_users', fixture=temp_path,
                             stdout=StringIO(), stderr=StringIO())
        finally:
            os.unlink(temp_path)

    def test_reject_fixture_with_duplicate_email(self):
        """Test rechazo de fixture con email duplicado — Requirement 7.6."""
        with open(self.FIXTURE_PATH, encoding='utf-8') as f:
            fixture_data = json.load(f)

        # Duplicar el primer usuario con pk diferente
        first_user = next(e for e in fixture_data if e.get('model') == 'core.user')
        duplicate = {
            'model': first_user['model'],
            'pk': 9999,
            'fields': dict(first_user['fields']),  # mismo email
        }
        modified = fixture_data + [duplicate]

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False, encoding='utf-8'
        ) as tmp:
            json.dump(modified, tmp, ensure_ascii=False)
            temp_path = tmp.name

        try:
            with self.assertRaises(CommandError):
                call_command('load_demo_users', fixture=temp_path,
                             stdout=StringIO(), stderr=StringIO())
        finally:
            os.unlink(temp_path)


class HomeProfileRolesIntegrationTest(TestCase):
    """
    Integration tests para exposición de perfil y roles en el sistema de autenticación.
    Valida: Requirements 9.1, 9.2, 9.3
    """

    def setUp(self):
        self.usuario_ic = CoreUser.objects.create_user(
            username='ic_int@test.com',
            email='ic_int@test.com',
            password='testpass123',
            first_name='Diego',
            last_name='Integración',
            perfil='Usuario IC',
        )
        role, _ = Role.objects.get_or_create(name='Redactor')
        self.usuario_ic.roles.add(role)

        self.usuario = CoreUser.objects.create_user(
            username='user_int@test.com',
            email='user_int@test.com',
            password='testpass123',
            first_name='Pablo',
            last_name='Integración',
            perfil='Usuario',
        )

    def test_home_context_includes_perfil_and_roles_after_auth(self):
        """
        Req 9.1, 9.2, 9.3: Al autenticarse, home incluye perfil y roles en el contexto.
        """
        self.client.login(username='ic_int@test.com', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('perfil', response.context)
        self.assertEqual(response.context['perfil'], 'Usuario IC')
        self.assertIn('roles', response.context)
        self.assertIn('ps_user_data', response.context)
        self.assertEqual(response.context['ps_user_data']['perfil'], 'Usuario IC')
        self.assertIn('Redactor', response.context['ps_user_data']['roles'])

    def test_usuario_ic_with_roles_sees_roles_in_template(self):
        """
        Req 9.2, 9.3: Usuario IC con roles ve los roles renderizados en home.html.
        """
        self.client.login(username='ic_int@test.com', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Redactor')

    def test_usuario_without_roles_no_roles_section_visible(self):
        """
        Req 9.3: Usuario sin roles no tiene roles en el contexto ni ve la sección de roles.
        """
        self.client.login(username='user_int@test.com', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['perfil'], 'Usuario')
        self.assertEqual(list(response.context['roles']), [])
        self.assertEqual(response.context['ps_user_data']['roles'], [])


# ─── Unit tests: home-chat-orchestrator-contract / ConversationIdManager ─────

from core.helpers.conversation import ConversationIdManager, _to_base36
from core.helpers.user_object import UserObjectBuilder
from core.helpers.html_sanitizer import HTMLSanitizer


class MockSession(dict):
    """Minimal session mock that behaves like Django's session."""
    modified = False


class ConversationIdManagerTest(TestCase):

    # ── _to_base36 ────────────────────────────────────────────────────────────

    def test_base36_zero(self):
        self.assertEqual(_to_base36(0), '0')

    def test_base36_thirty_five(self):
        self.assertEqual(_to_base36(35), 'z')

    def test_base36_thirty_six(self):
        self.assertEqual(_to_base36(36), '10')

    def test_base36_only_valid_chars(self):
        valid = set('0123456789abcdefghijklmnopqrstuvwxyz')
        for n in [1, 100, 1000, 999999]:
            result = _to_base36(n)
            self.assertTrue(set(result).issubset(valid), f"Invalid chars in {result!r}")

    # ── generate_conversation_id ──────────────────────────────────────────────

    def test_generate_starts_with_conv(self):
        cid = ConversationIdManager.generate_conversation_id()
        self.assertTrue(cid.startswith('conv-'), f"Expected 'conv-' prefix, got {cid!r}")

    def test_generate_has_three_parts(self):
        cid = ConversationIdManager.generate_conversation_id()
        parts = cid.split('-')
        self.assertEqual(len(parts), 3, f"Expected 3 parts, got {parts}")

    def test_generate_random_suffix_length(self):
        cid = ConversationIdManager.generate_conversation_id()
        suffix = cid.split('-')[2]
        self.assertEqual(len(suffix), 6, f"Expected 6-char suffix, got {suffix!r}")

    def test_generate_random_suffix_chars(self):
        valid = set('abcdefghijklmnopqrstuvwxyz0123456789')
        for _ in range(5):
            cid = ConversationIdManager.generate_conversation_id()
            suffix = cid.split('-')[2]
            self.assertTrue(set(suffix).issubset(valid), f"Invalid chars in suffix {suffix!r}")

    def test_generate_uniqueness(self):
        ids = {ConversationIdManager.generate_conversation_id() for _ in range(10)}
        self.assertGreater(len(ids), 1, "All generated IDs were identical")

    # ── get_or_create ─────────────────────────────────────────────────────────

    def test_get_or_create_creates_when_missing(self):
        session = MockSession()
        cid = ConversationIdManager.get_or_create(session)
        self.assertIsNotNone(cid)
        self.assertTrue(cid.startswith('conv-'))
        self.assertEqual(session[ConversationIdManager.SESSION_KEY], cid)

    def test_get_or_create_sets_modified_when_creating(self):
        session = MockSession()
        ConversationIdManager.get_or_create(session)
        self.assertTrue(session.modified)

    def test_get_or_create_reuses_existing(self):
        session = MockSession()
        session[ConversationIdManager.SESSION_KEY] = 'conv-existing-abcdef'
        cid = ConversationIdManager.get_or_create(session)
        self.assertEqual(cid, 'conv-existing-abcdef')

    def test_get_or_create_does_not_overwrite_existing(self):
        session = MockSession()
        session[ConversationIdManager.SESSION_KEY] = 'conv-original-abc123'
        ConversationIdManager.get_or_create(session)
        self.assertEqual(session[ConversationIdManager.SESSION_KEY], 'conv-original-abc123')

    # ── reset ─────────────────────────────────────────────────────────────────

    def test_reset_generates_new_id(self):
        session = MockSession()
        session[ConversationIdManager.SESSION_KEY] = 'conv-old-aaaaaa'
        new_cid = ConversationIdManager.reset(session)
        self.assertNotEqual(new_cid, 'conv-old-aaaaaa')

    def test_reset_stores_new_id_in_session(self):
        session = MockSession()
        session[ConversationIdManager.SESSION_KEY] = 'conv-old-aaaaaa'
        new_cid = ConversationIdManager.reset(session)
        self.assertEqual(session[ConversationIdManager.SESSION_KEY], new_cid)

    def test_reset_sets_modified(self):
        session = MockSession()
        ConversationIdManager.reset(session)
        self.assertTrue(session.modified)

    def test_reset_new_id_has_valid_format(self):
        session = MockSession()
        new_cid = ConversationIdManager.reset(session)
        self.assertTrue(new_cid.startswith('conv-'))


# ─── Serializer tests: home-chat-orchestrator-contract ───────────────────────

_VALID_REQUEST = {
    'conversationId': 'conv-abc123-zz9999',
    'query': '¿Qué comunicaciones hay?',
    'timestamp': '2026-06-26T14:00:00Z',
    'user': {
        'userId': 1,
        'userEmail': 'test@example.com',
        'userName': 'Test User',
        'profile': 'Administrador',
        'roles': [],
        'memoryEnabled': True,
    },
    'agentType': 'auto',
}

_VALID_RESPONSE = {
    'conversationId': 'conv-abc123-zz9999',
    'output': '<p>Respuesta</p>',
    'html_render': True,
    'metadata': {
        'agent_used': 'rag-mails',
        'execution_time_ms': 450,
        'records_found': 3,
    },
}


class RequestPayloadSerializerTest(TestCase):

    def _payload(self, **overrides):
        import copy
        data = copy.deepcopy(_VALID_REQUEST)
        data.update(overrides)
        return data

    def _user(self, **overrides):
        import copy
        user = copy.deepcopy(_VALID_REQUEST['user'])
        user.update(overrides)
        return user

    # ── criterio 1: payload válido pasa ──────────────────────────────────────

    def test_valid_payload_passes(self):
        """Payload completo y correcto es válido (criterio 1)"""
        s = RequestPayloadSerializer(data=_VALID_REQUEST)
        self.assertTrue(s.is_valid(), s.errors)

    # ── criterio 2: campos requeridos faltantes fallan ────────────────────────

    def test_missing_query_fails(self):
        """Falta query → error en campo query (criterio 2)"""
        data = self._payload()
        del data['query']
        s = RequestPayloadSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('query', s.errors)

    def test_missing_user_fails(self):
        """Falta user → error en campo user (criterio 2)"""
        data = self._payload()
        del data['user']
        s = RequestPayloadSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('user', s.errors)

    def test_missing_conversation_id_fails(self):
        """Falta conversationId → error en ese campo (criterio 2)"""
        data = self._payload()
        del data['conversationId']
        s = RequestPayloadSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('conversationId', s.errors)

    def test_empty_query_fails(self):
        """query vacío → error en campo query (criterio 2)"""
        s = RequestPayloadSerializer(data=self._payload(query=''))
        self.assertFalse(s.is_valid())
        self.assertIn('query', s.errors)

    # ── criterio 3: tipos incorrectos fallan ──────────────────────────────────

    def test_incorrect_type_user_id_fails(self):
        """userId no entero → error en user.userId (criterio 3)"""
        data = self._payload(user=self._user(userId='not-an-int'))
        s = RequestPayloadSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('user', s.errors)

    def test_incorrect_type_memory_enabled_fails(self):
        """memoryEnabled con string inválido → error (criterio 3)"""
        data = self._payload(user=self._user(memoryEnabled='maybe'))
        s = RequestPayloadSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('user', s.errors)

    # ── criterio 4: conversationId inválido falla ─────────────────────────────

    def test_conversation_id_no_conv_prefix_fails(self):
        """conversationId sin prefijo 'conv-' → error (criterio 4)"""
        s = RequestPayloadSerializer(data=self._payload(conversationId='chat-abc-def'))
        self.assertFalse(s.is_valid())
        self.assertIn('conversationId', s.errors)

    def test_conversation_id_wrong_parts_fails(self):
        """conversationId con solo 2 partes → error (criterio 4)"""
        s = RequestPayloadSerializer(data=self._payload(conversationId='conv-abc'))
        self.assertFalse(s.is_valid())
        self.assertIn('conversationId', s.errors)

    def test_conversation_id_too_many_parts_fails(self):
        """conversationId con 4 partes → error (criterio 4)"""
        s = RequestPayloadSerializer(data=self._payload(conversationId='conv-abc-def-ghi'))
        self.assertFalse(s.is_valid())
        self.assertIn('conversationId', s.errors)

    # ── criterio 5: agentType inválido → fallback 'auto' ─────────────────────

    def test_invalid_agent_type_falls_back_to_auto(self):
        """agentType desconocido → validated value es 'auto' (criterio 5)"""
        s = RequestPayloadSerializer(data=self._payload(agentType='unknown-agent'))
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data['agentType'], 'auto')

    def test_valid_agent_type_rag_mails_passes(self):
        """agentType 'rag-mails' es válido y se conserva (criterio 5)"""
        s = RequestPayloadSerializer(data=self._payload(agentType='rag-mails'))
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data['agentType'], 'rag-mails')

    def test_missing_agent_type_defaults_to_auto(self):
        """agentType ausente → default 'auto' (criterio 5)"""
        data = self._payload()
        del data['agentType']
        s = RequestPayloadSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data['agentType'], 'auto')

    # ── criterio 6: profile inválido falla ───────────────────────────────────

    def test_invalid_profile_fails(self):
        """profile fuera de las 5 opciones válidas → error (criterio 6)"""
        data = self._payload(user=self._user(profile='Desconocido'))
        s = RequestPayloadSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('user', s.errors)

    def test_all_valid_profiles_pass(self):
        """Los 5 perfiles válidos son aceptados (criterio 6)"""
        profiles = ['Administrador', 'Usuario IC', 'Heavy user', 'Macro', 'Usuario']
        for profile in profiles:
            data = self._payload(user=self._user(profile=profile))
            s = RequestPayloadSerializer(data=data)
            self.assertTrue(s.is_valid(), f"Profile '{profile}' should be valid: {s.errors}")


class ResponsePayloadSerializerTest(TestCase):

    def _payload(self, **overrides):
        import copy
        data = copy.deepcopy(_VALID_RESPONSE)
        data.update(overrides)
        return data

    # ── criterio 7: payload válido pasa ──────────────────────────────────────

    def test_valid_response_passes(self):
        """Response completo y correcto es válido (criterio 7)"""
        s = ResponsePayloadSerializer(data=_VALID_RESPONSE)
        self.assertTrue(s.is_valid(), s.errors)

    def test_optional_error_field_passes(self):
        """Response con campo error opcional también es válido (criterio 7)"""
        data = self._payload(error='algo salió mal')
        s = ResponsePayloadSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_records_found_null_passes(self):
        """metadata.records_found puede ser null (criterio 7)"""
        import copy
        data = copy.deepcopy(_VALID_RESPONSE)
        data['metadata']['records_found'] = None
        s = ResponsePayloadSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    # ── criterio 8: metadata faltante falla ──────────────────────────────────

    def test_missing_metadata_fails(self):
        """Falta metadata → error en campo metadata (criterio 8)"""
        data = self._payload()
        del data['metadata']
        s = ResponsePayloadSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('metadata', s.errors)

    def test_missing_output_fails(self):
        """Falta output → error en campo output (criterio 8)"""
        data = self._payload()
        del data['output']
        s = ResponsePayloadSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('output', s.errors)

    def test_missing_agent_used_in_metadata_fails(self):
        """Falta metadata.agent_used → error (criterio 8)"""
        import copy
        data = copy.deepcopy(_VALID_RESPONSE)
        del data['metadata']['agent_used']
        s = ResponsePayloadSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('metadata', s.errors)


# ─── Unit tests: home-chat-orchestrator-contract / UserObjectBuilder ──────────


class UserObjectBuilderTest(TestCase):
    """
    Unit tests para UserObjectBuilder.
    Validates: Requirement 8 AC1-7 — construcción de User_Object desde request.user.
    """

    def _make_user(self, **kwargs):
        defaults = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'perfil': 'Administrador',
            'memoria_habilitada': True,
        }
        defaults.update(kwargs)
        email = defaults.pop('email')
        return CoreUser.objects.create_user(
            username=email,
            email=email,
            password='testpass123',
            **defaults
        )

    def test_complete_user_object_all_fields(self):
        """Construcción completa con todos los campos (Req 8 AC1-7)"""
        user = self._make_user()
        obj = UserObjectBuilder.build(user)
        self.assertEqual(obj['userId'], user.id)
        self.assertEqual(obj['userEmail'], 'test@example.com')
        self.assertEqual(obj['userName'], 'Test User')
        self.assertEqual(obj['profile'], 'Administrador')
        self.assertEqual(obj['roles'], [])
        self.assertEqual(obj['memoryEnabled'], True)

    def test_username_fallback_when_first_name_empty(self):
        """Fallback a user.username cuando first_name y last_name vacíos (Req 8 AC4)"""
        user = self._make_user(first_name='', last_name='')
        obj = UserObjectBuilder.build(user)
        self.assertEqual(obj['userName'], user.username)

    def test_username_fallback_when_only_last_name(self):
        """first_name='' + last_name no vacío → userName usa el last_name (strip)"""
        user = self._make_user(first_name='', last_name='Zurlo')
        obj = UserObjectBuilder.build(user)
        self.assertEqual(obj['userName'], 'Zurlo')

    def test_roles_empty_for_administrador(self):
        """Roles vacíos para Administrador incluso si tiene roles en DB (Req 8 AC6)"""
        user = self._make_user(perfil='Administrador')
        role, _ = Role.objects.get_or_create(name='Diseñador')
        user.roles.add(role)
        obj = UserObjectBuilder.build(user)
        self.assertEqual(obj['roles'], [])

    def test_roles_empty_for_heavy_user(self):
        """Roles vacíos para Heavy user"""
        user = self._make_user(perfil='Heavy user')
        obj = UserObjectBuilder.build(user)
        self.assertEqual(obj['roles'], [])

    def test_roles_empty_for_macro(self):
        """Roles vacíos para Macro"""
        user = self._make_user(perfil='Macro')
        obj = UserObjectBuilder.build(user)
        self.assertEqual(obj['roles'], [])

    def test_roles_empty_for_usuario(self):
        """Roles vacíos para Usuario"""
        user = self._make_user(perfil='Usuario')
        obj = UserObjectBuilder.build(user)
        self.assertEqual(obj['roles'], [])

    def test_roles_populated_for_usuario_ic(self):
        """Roles poblados para Usuario IC (Req 8 AC6)"""
        user = self._make_user(perfil='Usuario IC')
        role1, _ = Role.objects.get_or_create(name='Diseñador')
        role2, _ = Role.objects.get_or_create(name='Redactor')
        user.roles.set([role1, role2])
        obj = UserObjectBuilder.build(user)
        self.assertIn('Diseñador', obj['roles'])
        self.assertIn('Redactor', obj['roles'])
        self.assertEqual(len(obj['roles']), 2)

    def test_roles_empty_for_usuario_ic_no_roles(self):
        """Usuario IC sin roles asignados → lista vacía"""
        user = self._make_user(perfil='Usuario IC')
        obj = UserObjectBuilder.build(user)
        self.assertEqual(obj['roles'], [])

    def test_all_5_profiles_valid(self):
        """Los 5 perfiles producen un User_Object con el perfil correcto"""
        profiles = ['Administrador', 'Usuario IC', 'Heavy user', 'Macro', 'Usuario']
        for i, perfil in enumerate(profiles):
            email = f'profile_test_{i}@example.com'
            user = self._make_user(email=email, perfil=perfil)
            obj = UserObjectBuilder.build(user)
            with self.subTest(perfil=perfil):
                self.assertEqual(obj['profile'], perfil)

    def test_memory_enabled_true(self):
        """memoryEnabled=True (Req 8 AC7)"""
        user = self._make_user(memoria_habilitada=True)
        obj = UserObjectBuilder.build(user)
        self.assertTrue(obj['memoryEnabled'])

    def test_memory_enabled_false(self):
        """memoryEnabled=False (Req 8 AC7)"""
        user = self._make_user(memoria_habilitada=False)
        obj = UserObjectBuilder.build(user)
        self.assertFalse(obj['memoryEnabled'])

    def test_user_id_is_integer(self):
        """userId es un número entero (Req 8 AC1)"""
        user = self._make_user()
        obj = UserObjectBuilder.build(user)
        self.assertIsInstance(obj['userId'], int)

    def test_user_email_matches_django_email(self):
        """userEmail coincide con user.email (Req 8 AC2)"""
        user = self._make_user(email='specific@test.com')
        obj = UserObjectBuilder.build(user)
        self.assertEqual(obj['userEmail'], 'specific@test.com')


# ─── Unit tests: home-chat-orchestrator-contract / HTMLSanitizer ──────────────


class HTMLSanitizerTest(TestCase):
    """Tests unitarios para HTMLSanitizer — tarea 4.2 (seguridad XSS crítica)"""

    def test_empty_string_returns_empty(self):
        """Empty string retorna empty string (Req 4.2 AC8)"""
        self.assertEqual(HTMLSanitizer.sanitize(''), '')

    def test_allowed_tags_pass_through(self):
        """Tags permitidos pasan sin cambios (Req 4.2 AC1)"""
        html = '<p>Hello <strong>world</strong> <em>test</em></p>'
        result = HTMLSanitizer.sanitize(html)
        self.assertIn('<p>', result)
        self.assertIn('<strong>', result)
        self.assertIn('<em>', result)
        self.assertIn('Hello', result)

    def test_disallowed_tags_stripped_content_kept(self):
        """Tags no permitidos se eliminan pero el contenido queda (Req 4.2 AC2)"""
        html = '<table><tr><td>Cell content</td></tr></table>'
        result = HTMLSanitizer.sanitize(html)
        self.assertNotIn('<table>', result)
        self.assertNotIn('<td>', result)
        self.assertIn('Cell content', result)

    def test_script_tags_blocked(self):
        """Script tags se eliminan completamente (Req 4.2 AC3 — crítico XSS)"""
        html = '<script>alert("xss")</script>'
        result = HTMLSanitizer.sanitize(html)
        self.assertNotIn('<script>', result)
        self.assertNotIn('</script>', result)

    def test_onclick_event_handler_blocked(self):
        """Event handler onclick se elimina del elemento (Req 4.2 AC4)"""
        html = '<p onclick="alert(1)">Safe text</p>'
        result = HTMLSanitizer.sanitize(html)
        self.assertNotIn('onclick', result)
        self.assertIn('<p>', result)
        self.assertIn('Safe text', result)

    def test_onerror_event_handler_blocked(self):
        """Event handler onerror se elimina del elemento (Req 4.2 AC4)"""
        html = '<p onerror="alert(1)">Text</p>'
        result = HTMLSanitizer.sanitize(html)
        self.assertNotIn('onerror', result)
        self.assertIn('Text', result)

    def test_javascript_protocol_href_blocked(self):
        """href con javascript: protocol se elimina (Req 4.2 AC5 — crítico XSS)"""
        html = '<a href="javascript:alert(1)">Click here</a>'
        result = HTMLSanitizer.sanitize(html)
        self.assertNotIn('javascript:', result)
        self.assertIn('Click here', result)

    def test_https_protocol_allowed(self):
        """href con https: protocol se mantiene (Req 4.2 AC6)"""
        html = '<a href="https://example.com">Link</a>'
        result = HTMLSanitizer.sanitize(html)
        self.assertIn('https://example.com', result)

    def test_http_protocol_allowed(self):
        """href con http: protocol se mantiene (Req 4.2 AC6)"""
        html = '<a href="http://example.com">Link</a>'
        result = HTMLSanitizer.sanitize(html)
        self.assertIn('http://example.com', result)

    def test_mailto_protocol_allowed(self):
        """href con mailto: protocol se mantiene (Req 4.2 AC6)"""
        html = '<a href="mailto:user@example.com">Email</a>'
        result = HTMLSanitizer.sanitize(html)
        self.assertIn('mailto:user@example.com', result)

    def test_disallowed_attribute_style_removed(self):
        """Atributo style no permitido se elimina (Req 4.2 AC7)"""
        html = '<p style="color:red">Styled text</p>'
        result = HTMLSanitizer.sanitize(html)
        self.assertNotIn('style=', result)
        self.assertIn('Styled text', result)

    def test_allowed_class_attribute_kept(self):
        """Atributo class permitido se mantiene (Req 4.2 AC7)"""
        html = '<p class="highlight">Text</p>'
        result = HTMLSanitizer.sanitize(html)
        self.assertIn('class="highlight"', result)


# ─── Unit tests: home-chat-orchestrator-contract / N8nClient ─────────────────
from unittest.mock import patch, MagicMock
import requests as requests_lib
from core.clients.n8n_client import (
    N8nClient,
    N8nConnectionError,
    N8nTimeoutError,
    N8nInvalidResponseError,
)


class N8nClientTest(TestCase):
    """
    Unit tests para N8nClient.
    Usa unittest.mock para simular requests.post sin llamadas HTTP reales.
    Validates: Design - Testing Strategy, Task 6.2
    """

    WEBHOOK_URL = 'http://test-webhook.local/webhook'

    def setUp(self):
        self.n8n = N8nClient(self.WEBHOOK_URL)

    @patch('core.clients.n8n_client.requests.post')
    def test_successful_request_returns_response_data(self, mock_post):
        """Request exitoso retorna response_data (Req 6.2 criterio 1)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"output": "ok", "html_render": true}'
        mock_response.json.return_value = {"output": "ok", "html_render": True}
        mock_post.return_value = mock_response

        result = self.n8n.send({"query": "test"})

        self.assertEqual(result, {"output": "ok", "html_render": True})
        mock_post.assert_called_once_with(
            self.WEBHOOK_URL,
            json={"query": "test"},
            headers={'Content-Type': 'application/json'},
            timeout=30,
        )

    @patch('core.clients.n8n_client.requests.post')
    def test_timeout_raises_N8nTimeoutError(self, mock_post):
        """Timeout lanza N8nTimeoutError (Req 6.2 criterio 2)"""
        mock_post.side_effect = requests_lib.Timeout()

        with self.assertRaises(N8nTimeoutError):
            self.n8n.send({"query": "test"})

    @patch('core.clients.n8n_client.requests.post')
    def test_connection_error_raises_N8nConnectionError(self, mock_post):
        """Connection error lanza N8nConnectionError (Req 6.2 criterio 3)"""
        mock_post.side_effect = requests_lib.ConnectionError()

        with self.assertRaises(N8nConnectionError):
            self.n8n.send({"query": "test"})

    @patch('core.clients.n8n_client.requests.post')
    def test_non_200_status_raises_N8nConnectionError(self, mock_post):
        """Status != 200 lanza N8nConnectionError (Req 6.2 criterio 4)"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_post.return_value = mock_response

        with self.assertRaises(N8nConnectionError):
            self.n8n.send({"query": "test"})

    @patch('core.clients.n8n_client.requests.post')
    def test_empty_body_raises_N8nInvalidResponseError(self, mock_post):
        """Body vacío lanza N8nInvalidResponseError (Req 6.2 criterio 5)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b''
        mock_post.return_value = mock_response

        with self.assertRaises(N8nInvalidResponseError):
            self.n8n.send({"query": "test"})

    @patch('core.clients.n8n_client.requests.post')
    def test_invalid_json_raises_N8nInvalidResponseError(self, mock_post):
        """JSON inválido lanza N8nInvalidResponseError (Req 6.2 criterio 6)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'not-valid-json'
        mock_response.text = 'not-valid-json'
        mock_response.json.side_effect = ValueError("No JSON object could be decoded")
        mock_post.return_value = mock_response

        with self.assertRaises(N8nInvalidResponseError):
            self.n8n.send({"query": "test"})

    def test_missing_webhook_url_raises_ValueError(self):
        """N8N_WEBHOOK_URL no configurada lanza ValueError (Req 6.2 criterio 7)"""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('N8N_WEBHOOK_URL', None)
            with self.assertRaises(ValueError):
                N8nClient()


# ─── Integration tests: home-chat-orchestrator-contract / ChatView ────────────
class ChatViewIntegrationTest(TestCase):
    """
    Integration tests para chat_view (POST /api/chat/).
    Mockea N8nClient para aislar Django de n8n en tests.
    Validates: Design - Testing Strategy, Task 8.8
    """

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='chattest@example.com',
            email='chattest@example.com',
            password='testpass123',
            first_name='Chat',
            last_name='Tester',
            perfil='Administrador',
        )

    def _valid_n8n_response(self):
        return {
            'conversationId': 'conv-test00-abc123',
            'output': '<p>Test response</p>',
            'html_render': True,
            'metadata': {
                'agent_used': 'auto',
                'execution_time_ms': 100,
                'records_found': None,
            },
        }

    def _post_chat(self, query='Hola', agent_type=None):
        body = {'query': query}
        if agent_type:
            body['agentType'] = agent_type
        return self.client.post(
            '/api/chat/',
            data=json.dumps(body),
            content_type='application/json',
        )

    @patch('core.views.N8nClient')
    def test_authenticated_user_can_send_query(self, mock_n8n_class):
        """Usuario autenticado recibe 200 con estructura válida (Req 8.8 criterio 1)"""
        mock_client = MagicMock()
        mock_client.send.return_value = self._valid_n8n_response()
        mock_n8n_class.return_value = mock_client
        self.client.force_login(self.user)

        response = self._post_chat('¿Qué comunicaciones hay?')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('output', data)
        self.assertIn('html_render', data)
        self.assertIn('metadata', data)

    @patch('core.views.N8nClient')
    def test_conversation_id_generated_on_first_request(self, mock_n8n_class):
        """conversationId se genera y almacena en session en primera request (Req 8.8 criterio 2)"""
        mock_client = MagicMock()
        mock_client.send.return_value = self._valid_n8n_response()
        mock_n8n_class.return_value = mock_client
        self.client.force_login(self.user)

        response = self._post_chat('Primera consulta')

        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertIn('conversationId', session)
        self.assertTrue(session['conversationId'].startswith('conv-'))

    @patch('core.views.N8nClient')
    def test_conversation_id_reused_on_second_request(self, mock_n8n_class):
        """Requests sucesivas reutilizan el mismo conversationId de sesión (Req 8.8 criterio 3)"""
        mock_client = MagicMock()
        mock_client.send.return_value = self._valid_n8n_response()
        mock_n8n_class.return_value = mock_client
        self.client.force_login(self.user)

        self._post_chat('Primera')
        conv_id_1 = self.client.session['conversationId']

        self._post_chat('Segunda')
        conv_id_2 = self.client.session['conversationId']

        self.assertEqual(conv_id_1, conv_id_2)

    def test_unauthenticated_user_gets_redirect(self):
        """Usuario no autenticado recibe redirect (302) a login (Req 8.8 criterio 4)"""
        response = self._post_chat('Hola')
        self.assertEqual(response.status_code, 302)

    def test_empty_query_returns_400(self):
        """Query vacío recibe 400 Bad Request (Req 8.8 criterio 5)"""
        self.client.force_login(self.user)
        response = self._post_chat(query='')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_invalid_json_returns_400(self):
        """JSON inválido en body recibe 400 Bad Request (Req 8.8 criterio 6)"""
        self.client.force_login(self.user)
        response = self.client.post(
            '/api/chat/',
            data='not-valid-json{{{',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    @patch('core.views.N8nClient')
    def test_n8n_timeout_returns_504(self, mock_n8n_class):
        """N8n timeout retorna 504 Gateway Timeout (Req 8.8 criterio 7)"""
        mock_client = MagicMock()
        mock_client.send.side_effect = N8nTimeoutError('Request timed out')
        mock_n8n_class.return_value = mock_client
        self.client.force_login(self.user)

        response = self._post_chat('Consulta con timeout')

        self.assertEqual(response.status_code, 504)
        data = response.json()
        self.assertIn('error', data)

    @patch('core.views.N8nClient')
    def test_n8n_unavailable_returns_503(self, mock_n8n_class):
        """N8n no disponible retorna 503 Service Unavailable (Req 8.8 criterio 8)"""
        mock_client = MagicMock()
        mock_client.send.side_effect = N8nConnectionError('Could not connect')
        mock_n8n_class.return_value = mock_client
        self.client.force_login(self.user)

        response = self._post_chat('Consulta sin n8n')

        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertIn('error', data)
