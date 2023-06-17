from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


# Create your tests here.
class LoginTest(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_view(self):
        # teste para login válido
        login_url = reverse('user:login')
        response = self.client.post(login_url, {'username': 'testuser', 'password': 'testpassword'})
        self.assertTrue(response.status_code in [200, 302])

    def test_invalid_login(self):
        # teste para login inválido
        login_url = reverse('user:login')
        response = self.client.post(login_url, {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 401)


