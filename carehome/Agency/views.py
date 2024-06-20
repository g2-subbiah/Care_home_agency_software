from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.forms import AuthenticationForm
from .backends import GroupBasedBackend
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from .forms import UserRegistrationForm, ClientRegistrationForm
from django.utils.timezone import now
from django.contrib import messages
from django.core.management import call_command
from django.views import View
from django.urls import reverse
from django.utils.timezone import make_aware
from staff.models import WeekDateRange, TimeSheet
from datetime import timedelta
from staff.models import TimeSheet
import csv


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


class WeeklyReportView(View):
    template_name = 'agency/weekly_report.html'

    def get(self, request):
        # Retrieve available years and week numbers for dropdown
        week_date_ranges = WeekDateRange.objects.all().order_by('year', 'week_number')
        context = {
            'week_date_ranges': week_date_ranges,

        }
        return render(request, self.template_name, context)

    def post(self, request):
        year = request.POST.get('year')
        week_number = request.POST.get('week_number')

        # Retrieve TimeSheet entries for the selected week
        timesheets = TimeSheet.objects.filter(
            date_of_work__gte=WeekDateRange.objects.get(year=year, week_number=week_number).start_date,
            date_of_work__lte=WeekDateRange.objects.get(year=year, week_number=week_number).end_date
        )

        # Export the retrieved data to CSV
        response = HttpResponse(content_type='text/csv')
        csv_filename = f'weekly_report_week_{week_number}.csv'
        response['Content-Disposition'] = f'attachment; filename="{csv_filename}"'

        writer = csv.writer(response)
        writer.writerow(['User', 'Date of Work', 'Shift Started Time', 'Break Started Time', 'Break Finished Time', 'Shift Finished Time', 'Client Rep Name', 'Client Rep Position'])

        for timesheet in timesheets:
            writer.writerow([
                timesheet.user.get_full_name(),
                timesheet.date_of_work,
                timesheet.shift_started_time,
                timesheet.break_started_time,
                timesheet.break_finished_time,
                timesheet.shift_finished_time,
                timesheet.client_rep_name,
                timesheet.client_rep_position,
            ])

        # Clear entries from TimeSheet for the selected week
        timesheets.delete()

        return response
        


class ClearTimeSheetsView(View):

    def post(self, request):
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        try:
            # Delete TimeSheet entries for the selected week
            TimeSheet.objects.filter(date_of_work__range=[start_date, end_date]).delete()

            # Redirect back to the weekly report page or any other appropriate page
            return redirect('weekly_report')

        except Exception as e:
            # Handle any errors during deletion
            return redirect('weekly_report')


