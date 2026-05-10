from django.contrib.auth import get_user_model
from django.test import TestCase

from config.allauth_adapter import CustomSocialAccountAdapter


class FakeAccount:
    extra_data = {"email": "USER@Example.COM"}


class FakeSocialLogin:
    is_existing = False

    def __init__(self, user):
        self.user = user
        self.account = FakeAccount()
        self.connected_user = None

    def connect(self, request, user):
        self.connected_user = user


class CustomSocialAccountAdapterTests(TestCase):
    def test_pre_social_login_connects_existing_user_by_email_case_insensitive(self):
        user_model = get_user_model()
        existing_user = user_model.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="test-password",
        )
        social_user = user_model(email="USER@example.com")
        sociallogin = FakeSocialLogin(social_user)

        CustomSocialAccountAdapter().pre_social_login(None, sociallogin)

        self.assertEqual(sociallogin.connected_user, existing_user)
