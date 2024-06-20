# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.forms import AuthenticationForm
from Agency.models import CustomUser
from django.contrib.auth import logout
from Agency.backends import GroupBasedBackend
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import TimeSheetForm
from client.views import clientlogin
from datetime import datetime
from .models import TimeSheet
from django.utils.timezone import make_aware
from .findweek import get_week_date_range
from django.urls import reverse
from django.utils.timezone import now
from django.contrib import messages
from django.core.management import call_command

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



@login_required
def submit_timesheet(request):
    if request.method == 'POST':
        form = TimeSheetForm(request.POST, request.FILES)
        if form.is_valid():
            timesheet = form.save(commit=False)
            timesheet.user = request.user  # Set the logged-in user
            timesheet.save()

            return redirect('success-page')
        else:
            print(form.errors)
            return HttpResponseBadRequest("Form data is invalid.")
    else:
        form = TimeSheetForm()

    return render(request, 'staff/timesheet.html', {'form': form})


def success_page(request):
    return render(request, 'staff/success_timesheet.html')

def success_weekcreation(request):
    return render(request, 'agency/success_weekcreation.html')


def retrieve_timesheets_for_week(request, year, week_number):
    start_of_week, end_of_week = get_week_date_range(year, week_number)

    # Make dates timezone-aware if necessary
    start_of_week = make_aware(datetime.datetime.combine(start_of_week, datetime.time.min))
    end_of_week = make_aware(datetime.datetime.combine(end_of_week, datetime.time.max))

    weekly_timesheets = TimeSheet.objects.filter(date_of_work__range=(start_of_week, end_of_week))

    context = {
        'weekly_timesheets': weekly_timesheets,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
    }
    return render(request, 'staff/weekly_timesheets.html', context)


def create_weeks_table_view(request, year):
    if request.method == 'POST':
        # Call the management command to populate WeekDateRange table
        try:
            call_command('populate_weeks', str(year), str(year + 1))
            messages.success(request, f'Successfully created weeks for {year}-{year + 1}')
        except Exception as e:
            messages.error(request, f'Failed to create weeks: {str(e)}')
        
        # Redirect back to some page or render a template as needed
        return redirect('success_weekcreation')  # Replace with the appropriate URL name or path
    
    # Render a template with a button to trigger the creation of weeks
    context = {
        'year': year,
    }
    return render(request, 'agency/create_weeks.html', context)







