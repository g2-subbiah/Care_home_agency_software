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
from staff.models import WeekDateRange
from datetime import datetime, timedelta, date
from .forms import WeekForm
from .requirement import SubmitRequirementView
from django.views.generic import TemplateView
from django.views.generic import View



def clientlogin(request):
    users = CustomUser.objects.filter(groups__name='client')  # Retrieving client users
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = GroupBasedBackend().authenticate(request, username=username, password=password, group='client')
            if user is not None:
                if hasattr(user, 'needs_password_change') and user.needs_password_change:
                    login(request, user)
                    return redirect('change-password2')  # Redirecting to the password change page
                else:
                    login(request, user)
                    return redirect('client-front')  # Redirecting to client home page
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
            return redirect('client-login')  # Redirecting to client home page after changing password
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'client/change_password2.html', {'form': form})

class SuccessRequirementView(View):
    template_name = 'client/success_requirement.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


    
