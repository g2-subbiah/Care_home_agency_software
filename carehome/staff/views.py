# views.py
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

def stafflogin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = GroupBasedBackend().authenticate(request, username=username, password=password, group='staff')
            if user is not None:
                if hasattr(user, 'needs_password_change') and user.needs_password_change:
                    login(request, user)
                    return redirect('change-password')  # Redirect to the password change page
                else:
                    login(request, user)
                    return redirect('staff-front')  # Redirect to staff home page
            else:
                return HttpResponse("Invalid login credentials or unauthorized access")
    else:
        form = AuthenticationForm()
    return render(request, 'staff/staffloginpage.html', {'form': form})

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            user.needs_password_change = False
            user.save()
            return redirect('staff-login')  # Redirect to staff home page after changing password
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'staff/change_password.html', {'form': form})

def staff_front(request):
    context = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    }
    return render(request, "staff/stafffrontpage.html", context)

def timesheet(request):
    return render(request, "staff/timesheet.html")
