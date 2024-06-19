from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.forms import AuthenticationForm
from .backends import GroupBasedBackend
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from .forms import UserRegistrationForm, ClientRegistrationForm

from .models import CustomUser
from django.contrib.auth import get_user_model, logout

User = get_user_model()

def home(request):
    return render(request,"home.html")

def forgetpw(request):
    return render(request,"agency/forgetpw.html")

def agency_front(request):
    return render(request, "agency/agencyfrontpage.html")

def agencylogin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = GroupBasedBackend().authenticate(request, username=username, password=password, group='Agency')
            if user is not None:
                login(request, user)
                return redirect('agency-front')  # Redirect to the agency home page
            else:
                return HttpResponse("Invalid login credentials or unauthorized access")
    else:
        form = AuthenticationForm()
    return render(request, 'agency/agencyloginpage.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.needs_password_change = True
            user.save()
            staff_group = Group.objects.get(name='staff')
            user.groups.add(staff_group)
            return redirect('staff-login')
        else:
            return render(request, 'agency/register.html', {'form': form})
        
    else:
        form = UserRegistrationForm()
        return render(request, 'agency/register.html', {'form': form})
    

def register_client(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.needs_password_change = True
            user.save()
            client_group = Group.objects.get(name='client')
            user.groups.add(client_group)
            return redirect('client-login')
        else:
            return render(request, 'client/client_register.html', {'form': form})
        
    else:
        form = ClientRegistrationForm()
        return render(request, 'client/client_register.html', {'form': form})



def agency_logout(request):
    logout(request)
    return redirect('home-page')
