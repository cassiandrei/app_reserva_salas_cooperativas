from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


# Create your tests here.
class LoginTest(TestCase):
    def setUp(self):
        # usuario ativo
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

        # usuário inativo
        self.username = "testuser_inativo"
        self.password = "testpassword2"
        self.user2 = User.objects.create_user(
            username=self.username, password=self.password, is_active=False
        )

    def test_login_view(self):
        # teste para login válido
        login_url = reverse("user:login")
        response = self.client.post(
            login_url, {"username": "testuser", "password": "testpassword"}
        )
        self.assertTrue(response.status_code in [200, 302])

    def test_login_view_get_inputs(self):
        # teste para verificar se os inputs estão aparecendo
        login_url = reverse("user:login")

        # realiza o GET no /user/login
        response = self.client.get(login_url)

        self.assertContains(
            response,
            'id="id_username"',
            msg_prefix="Tela de login não exibiu o input de username",
        )
        self.assertContains(
            response,
            'id="id_password"',
            msg_prefix="Tela de login não exibiu o input de password",
        )
        self.assertContains(
            response,
            'id="login_button"',
            msg_prefix="Tela de login não exibiu o button de submit",
        )

    def test_invalid_login(self):
        # teste para login inválido
        login_url = reverse("user:login")
        response = self.client.post(
            login_url, {"username": "testuser", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 401)

    def test_inactive_login(self):
        # teste para login de usário inativa
        login_url = reverse("user:login")
        response = self.client.post(
            login_url, {"username": "testuser_inativo", "password": "testpassword2"}
        )
        self.assertEqual(response.status_code, 401)
