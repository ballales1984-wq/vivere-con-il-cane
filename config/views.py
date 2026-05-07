from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
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
