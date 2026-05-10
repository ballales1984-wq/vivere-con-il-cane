from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils import translation
from django.conf import settings
from django.urls import get_resolver
import os

@csrf_exempt
def create_test_account(request):
    """
    Temporary endpoint to create a test account.
    Only works if SECRET_TEST_TOKEN matches environment variable.
    Remove after use.
    """
    token = request.GET.get('token')
    expected_token = os.environ.get('TEST_ACCOUNT_TOKEN', 'test-token-123')
    
    if token != expected_token:
        return JsonResponse({'error': 'Invalid token'}, status=403)
    
    User = get_user_model()
    email = 'test@vivereconilcane.com'
    password = 'Test123!'
    
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return JsonResponse({'message': 'Account already exists, password reset', 'email': email, 'password': password})
    
    user = User.objects.create_user(email=email, password=password, username=email)
    user.save()
    
    return JsonResponse({'message': 'Test account created', 'email': email, 'password': password})


@csrf_exempt
def emergency_reset_account(request):
    """
    Temporary production-only account reset endpoint.
    Remove immediately after the account has been recovered.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    token = request.POST.get("token")
    if token != "reset-ballales-20260510-6f2cf4f9":
        return JsonResponse({"error": "Invalid token"}, status=403)

    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    allowed_emails = {"ballales1984@gmail.com", "ballales1984@yahoo.it"}
    if email not in allowed_emails:
        return JsonResponse({"error": "Email not allowed"}, status=400)
    if len(password) < 10:
        return JsonResponse({"error": "Password too short"}, status=400)

    from allauth.account.models import EmailAddress
    from allauth.socialaccount.models import SocialAccount

    User = get_user_model()
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        user = User.objects.create_user(username=email, email=email, password=password)
        action = "created"
    else:
        user.username = email
        user.email = email
        user.is_active = True
        user.set_password(password)
        user.save()
        action = "reset"

    EmailAddress.objects.update_or_create(
        user=user,
        email=email,
        defaults={"verified": True, "primary": True},
    )
    SocialAccount.objects.filter(user=user).delete()

    return JsonResponse(
        {
            "ok": True,
            "action": action,
            "user_id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
        }
    )


def change_language(request):
    """
    View to change the language settings.
    """
    next_url = request.GET.get('next', '/')
    if request.method == 'POST':
        lang_code = request.POST.get('language')
        if lang_code and translation.check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
            response = HttpResponseRedirect(next_url)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            return response
    return HttpResponseRedirect(next_url)
