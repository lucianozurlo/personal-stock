from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist

# ─── Property-based tests: usuarios-demo-perfiles-permisos ───────────────────
from hypothesis import given, settings as hyp_settings
from hypothesis import strategies as st
from hypothesis.extra.django import TestCase as HypothesisTestCase

from core.models import User as CoreUser, Role  # Requiere AUTH_USER_MODEL + migración (tareas 3.1, 3.2)

hyp_settings.register_profile("usuarios", max_examples=100, deadline=1000)
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
