from django.shortcuts import render , redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.shortcuts import render, redirect
from .models import UserExtraFields
from .utils import verify_password , username_exists

def hide_and_show_api_keys(request):
    print("hide_and_show_api_keys")
    user = request.user
    user_extra = UserExtraFields.objects.get(user=user)
    user_extra.hide_api_key = not user_extra.hide_api_key
    user_extra.save()
    return redirect('profile')
    #     user = request.user
    #     user_extra = UserExtraFields.objects.get(user=user)
    #     user_extra.hide_api_key = not user_extra.hide_api_key
    #     user_extra.save()
    #     return redirect('profile')
    # else:
    #     return redirect('profile')

def login_for_migration_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username_exists(username) and verify_password(username, password):
            # Use Django's built-in authentication system to get the user
            user = get_user_model().objects.get(username=username)
            # Use Django's set_password method to securely hash and store the new password
            user.set_password(password)
            user.save()
            print("User password updated")
            return redirect("account_login")
        else:
            return render(request, 'accounts/migration_user_login.html', {'error': 'Invalid username or password'})
    return render(request, 'accounts/migration_user_login.html')
