from urllib import response
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class AuthAppPositiveTests(TestCase):
    def setUp(self):
        self.registration_url = reverse("register")
        self.login_url = reverse("login")
        self.refresh_url = reverse("token_refresh")
        self.logout_url = reverse("logout")

        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "confirmed_password": "testpassword123"
        }

    def test_user_registration(self):
        response = self.client.post(self.registration_url, self.user_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(set(response.data.keys()), {
                         "message", "uid", "token"})

        User = get_user_model()
        self.assertTrue(User.objects.filter(
            email=self.user_data["email"]).exists())

        user = User.objects.get(email=self.user_data["email"])
        self.assertFalse(user.is_active)

    def test_user_login(self):
        self.client.post(self.registration_url, self.user_data)

        User = get_user_model()
        user = User.objects.get(email=self.user_data["email"])
        user.is_active = True
        user.save()

        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.cookies)
        self.assertIn("refresh", response.cookies)

    def test_user_logout(self):
        self.client.post(self.registration_url, self.user_data)
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        self.client.post(self.login_url, login_data)

        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, 200)
        response.delete_cookie("access")
        response.delete_cookie("refresh")

    def test_token_refresh(self):
        self.client.post(self.registration_url, self.user_data)
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        self.client.post(self.login_url, login_data)

        response = self.client.post(self.refresh_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.cookies)

    def test_password_reset(self):
        self.client.post(self.registration_url, self.user_data)

        password_reset_url = reverse("password_reset")
        reset_data = {"email": self.user_data["email"]}
        response = self.client.post(password_reset_url, reset_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"],
                         "Password reset email sent.")

    def test_password_reset_confirm(self):
        self.client.post(self.registration_url, self.user_data)
        User = get_user_model()
        user = User.objects.get(email=self.user_data["email"])

        password_reset_url = reverse("password_reset")
        reset_data = {"email": self.user_data["email"]}
        self.client.post(password_reset_url, reset_data)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        password_reset_confirm_url = reverse(
            "password_reset_confirm", args=[uid, token])
        new_password_data = {
            "new_password": "newtestpassword123",
            "confirmed_password": "newtestpassword123"
        }
        response = self.client.post(
            password_reset_confirm_url, new_password_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"],
                         "Password has been reset successfully.")

        login_data = {
            "email": self.user_data["email"],
            "password": "newtestpassword123"
        }
        login_response = self.client.post(self.login_url, login_data)
        self.assertEqual(login_response.status_code, 200)


class AuthAppNegativeTests(TestCase):
    def setUp(self):
        self.registration_url = reverse("register")
        self.login_url = reverse("login")

        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123"
        }

    def test_user_registration_with_existing_email(self):
        self.client.post(self.registration_url, self.user_data)

        response = self.client.post(self.registration_url, self.user_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["email"][0], "Email already exists")

    def test_user_registration_with_mismatched_passwords(self):
        invalid_user_data = self.user_data.copy()
        invalid_user_data["confirmed_password"] = "differentpassword"

        response = self.client.post(self.registration_url, invalid_user_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["confirmed_password"][0], "Passwords do not match")

    def test_user_login_without_activation(self):
        self.client.post(self.registration_url, self.user_data)

        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["error"], "Account is not activated.")

    def test_user_login_with_incorrect_password(self):
        self.client.post(self.registration_url, self.user_data)

        User = get_user_model()
        user = User.objects.get(email=self.user_data["email"])
        user.is_active = True
        user.save()

        login_data = {
            "email": self.user_data["email"],
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["error"], "Invalid credentials.")

    def test_user_login_with_nonexistent_email(self):
        login_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword"
        }
        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["error"], "Invalid credentials.")

    def test_password_reset_with_nonexistent_email(self):
        password_reset_url = reverse("password_reset")
        reset_data = {"email": "nonexistent@example.com"}
        response = self.client.post(password_reset_url, reset_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["email"][0], "Email does not exist.")

    def test_password_reset_confirm_with_invalid_token(self):
        self.client.post(self.registration_url, self.user_data)
        User = get_user_model()
        user = User.objects.get(email=self.user_data["email"])

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        invalid_token = "invalid-token"

        password_reset_confirm_url = reverse(
            "password_reset_confirm", args=[uid, invalid_token])
        new_password_data = {
            "new_password": "newtestpassword123",
            "confirmed_password": "newtestpassword123"
        }
        response = self.client.post(
            password_reset_confirm_url, new_password_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Invalid token or UID.")