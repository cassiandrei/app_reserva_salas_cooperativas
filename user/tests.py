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
        login_url = reverse('user:login')
        response = self.client.post(login_url, {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)

    def test_invalid_login(self):
        login_url = reverse('user:login')
        response = self.client.post(login_url, {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertNotEqual(response.status_code, 200)



