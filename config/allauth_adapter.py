"""Custom django-allauth adapters for Vivere con il Cane."""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


User = get_user_model()


def normalize_email(email):
    return email.strip().lower() if email else email


def sync_username_with_email(user):
    if user.email:
        user.email = normalize_email(user.email)
        user.username = user.email


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom adapter to handle email-based authentication"""

    def save_user(self, request, user, form, commit=True):
        """Override to ensure email is properly saved, password is set, and username is synced"""
        # Use parent implementation to properly set email and password
        user = super().save_user(request, user, form, commit=False)
        # Ensure username equals email for consistency
        sync_username_with_email(user)
        if commit:
            user.save()
        return user

    def populate_username(self, request, user):
        """Ensure username is set to email for consistency"""
        sync_username_with_email(user)

    def is_open_for_signup(self, request):
        """Always allow signups"""
        return True

    def clean_email(self, email):
        """Ensure email is valid and unique"""
        email = normalize_email(super().clean_email(email))
        if email and '@' in email:
            user_pk = getattr(getattr(self, 'user', None), 'pk', None)
            if User.objects.filter(email__iexact=email).exclude(pk=user_pk).exists():
                raise ValidationError(
                    "A user is already registered with this email address."
                )
        return email


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Connect Google sign-ins to existing users with the same email."""

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        email = normalize_email(user.email or sociallogin.account.extra_data.get("email"))
        if email:
            user.email = email
            user.username = email
        if not user.first_name:
            user.first_name = sociallogin.account.extra_data.get("given_name", "")
        if not user.last_name:
            user.last_name = sociallogin.account.extra_data.get("family_name", "")
        return user

    def pre_social_login(self, request, sociallogin):
        """
        If a user with the same email already exists, connect the social account to that user.
        """
        if sociallogin.is_existing:
            return

        email = normalize_email(sociallogin.user.email)
        if not email:
            email = normalize_email(sociallogin.account.extra_data.get("email"))
        if not email:
            return

        existing_user = User.objects.filter(email__iexact=email).first()
        if existing_user:
            sociallogin.connect(request, existing_user)
            sync_username_with_email(existing_user)
            existing_user.save(update_fields=["email", "username"])

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        sync_username_with_email(user)
        user.save(update_fields=["email", "username"])
        return user

