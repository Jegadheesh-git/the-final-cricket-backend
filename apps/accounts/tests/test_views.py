from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User

class AuthViewsTest(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.me_url = reverse('me')
        self.user_data = {
            "username": "testauth",
            "email": "auth@test.com",
            "password": "strongpassword123"
        }

    def test_registration_success(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testauth").exists())
        # Check auto-login session
        self.assertIn("_auth_user_id", self.client.session)

    def test_registration_duplicate(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        User.objects.create_user(**self.user_data)
        login_data = {
            "username": "testauth",
            "password": "strongpassword123"
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_failure(self):
        User.objects.create_user(**self.user_data)
        login_data = {
            "username": "testauth",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me_view_authenticated(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_login(user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testauth")

    def test_me_view_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
