from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist


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
