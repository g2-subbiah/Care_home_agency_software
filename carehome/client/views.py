from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.forms import AuthenticationForm
from Agency.models import CustomUser
from django.contrib.auth import logout
from Agency.backends import GroupBasedBackend
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


def clientlogin(request):
    users = CustomUser.objects.filter(groups__name='client')  # Retrieve client users
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = GroupBasedBackend().authenticate(request, username=username, password=password, group='client')
            if user is not None:
                if hasattr(user, 'needs_password_change') and user.needs_password_change:
                    login(request, user)
                    return redirect('change-password2')  # Redirect to the password change page
                else:
                    login(request, user)
                    return redirect('client-front')  # Redirect to client home page
            else:
                return HttpResponse("Invalid login credentials or unauthorized access")
    else:
        form = AuthenticationForm()
    return render(request, 'client/clientloginpage.html', {'form': form, 'users': users})

def change_password2(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            user.needs_password_change = False
            user.save()
            return redirect('client-login')  # Redirect to client home page after changing password
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'client/change_password2.html', {'form': form})

def client_front(request):
    context = {
        'first_name': request.user.first_name,
    }
    return render(request, "client/clientfrontpage.html", context)



