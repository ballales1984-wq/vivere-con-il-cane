"""
Custom Allauth Adapter for Vivere con il Cane
Ensures email is used as username and properly populated in the email field
"""
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom adapter to handle email-based authentication"""
    
    def save_user(self, request, user, form, commit=True):
        """Override to ensure email is properly saved and username is synced"""
        data = form.cleaned_data
        email = data.get('email')
        
        # Set username to email (for consistency and authentication)
        if email:
            user.username = email
            user.email = email
        
        if commit:
            user.save()
        return user
    
    def populate_username(self, request, user):
        """Ensure username is set to email for consistency"""
        if user.email:
            user.username = user.email
            user.save(update_fields=['username'])

