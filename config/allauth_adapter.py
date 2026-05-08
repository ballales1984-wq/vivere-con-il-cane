"""
Custom Allauth Adapter for Vivere con il Cane
Ensures email is used as username and properly populated in the email field
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter, DefaultSocialAccountAdapter):
    """Custom adapter to handle email-based authentication"""

    def populate_user(self, request, sociallogin, data):
        """
        Hook to populate the user instance from sociallogin data.
        This method is called when creating a new user via social account.
        """
        user = super().populate_user(request, sociallogin, data)
        # Set email from sociallogin account if not already set
        if not user.email:
            email = sociallogin.account.extra_data.get('email')
            if email:
                user.email = email
        # Optionally set first and last name
        if not user.first_name:
            user.first_name = sociallogin.account.extra_data.get('given_name', '')
        if not user.last_name:
            user.last_name = sociallogin.account.extra_data.get('family_name', '')
        return user

    def save_user(self, request, user, form, commit=True):
        """Override to ensure email is properly saved, password is set, and username is synced"""
        # Use parent implementation to properly set email and password
        user = super().save_user(request, user, form, commit=False)
        # Ensure username equals email for consistency
        if user.email:
            user.username = user.email
        if commit:
            user.save()
        return user

    def populate_username(self, request, user):
        """Ensure username is set to email for consistency"""
        if user.email and not user.username:
            user.username = user.email
            user.save(update_fields=['username'])

    def is_open_for_signup(self, request):
        """Always allow signups"""
        return True

    def clean_email(self, email):
        """Ensure email is valid and unique"""
        email = super().clean_email(email)
        if email and '@' in email:
            user_pk = getattr(getattr(self, 'user', None), 'pk', None)
            if User.objects.filter(email=email).exclude(pk=user_pk).exists():
                raise ValidationError(
                    "A user is already registered with this email address."
                )
        return email

    def pre_social_login(self, request, sociallogin):
        """
        If a user with the same email already exists, connect the social account to that user.
        """
        user = sociallogin.user
        if user.is_anonymous:
            # Check if there's a user with the same email
            if user.email:
                existing_user = User.objects.filter(email=user.email).first()
                if existing_user:
                    # Connect the social account to the existing user
                    sociallogin.connect(request, existing_user)
                    # Update the user's username to match the email (if needed)
                    existing_user.username = existing_user.email
                    existing_user.save()

