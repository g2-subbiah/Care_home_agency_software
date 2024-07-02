from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views import View
from django.db.models import F, ExpressionWrapper, DurationField
from django.conf import settings
from datetime import datetime, timedelta, date
from staff.models import TimeSheet, WeekDateRange
from django.db.models.functions import ExtractMonth, ExtractYear
from Agency.models import CustomUser
import calendar


class TimesheetTableView(View):
    template_name = 'agency/timesheets_view.html'

    def get(self, request):
        years = range(2024, datetime.now().year + 1)
        week_date_ranges = WeekDateRange.objects.all()
        client_usernames = CustomUser.objects.filter(groups__name='client').values_list('first_name', flat=True)
        staff_names = CustomUser.objects.filter(groups__name='staff').values_list('first_name', flat=True)
        #staff_names = [f"{first_name} {last_name}" for first_name, last_name in staff_names]
        months = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
            7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        context = {
            'years': years,
            'week_date_ranges': week_date_ranges,
            'client_usernames': client_usernames,
            'staff_names': staff_names,
            'months': months
        }
        return render(request, self.template_name, context)

    def post(self, request):
        action = request.POST.get('action')

        if action == 'generate_weekly_report':
            return self.generate_weekly_report(request)
        elif action == 'generate_monthly_report':
            return self.generate_monthly_report(request)
        else:
            return HttpResponseBadRequest('Invalid action parameter')

    def get_week_date_ranges(self, year):
        week_date_ranges = WeekDateRange.objects.filter(year=year).order_by('start_date')
        return week_date_ranges

    def generate_weekly_report(self, request):
        year = request.POST.get('year')
        week_number = request.POST.get('week_number')
        staff_name = request.POST.get('staff_name')

        if not year or not week_number or not staff_name:
            return HttpResponseBadRequest('Year, week number, and staff name are required.')

        try:
            year = int(year)
            week_number = int(week_number)
        except ValueError:
            return HttpResponseBadRequest('Invalid year or week number.')

        # Fetch timesheets for the selected week and staff
        try:
            start_date = WeekDateRange.objects.get(year=year, week_number=week_number).start_date
            end_date = WeekDateRange.objects.get(year=year, week_number=week_number).end_date
        except WeekDateRange.DoesNotExist:
            return HttpResponseBadRequest('Invalid week number or year.')

        timesheets = TimeSheet.objects.filter(
            date_of_work__gte=start_date,
            date_of_work__lte=end_date,
            user__first_name=staff_name
        ).order_by('care_home_name', 'date_of_work')

        # Calculate total worked hours for each timesheet entry
        timesheets = timesheets.annotate(
            total_worked_hours=ExpressionWrapper(
                F('shift_finished_time') - F('shift_started_time'),
                output_field=DurationField()
            )
        )

        context = {
            'timesheets': timesheets,
            'week_range': f"Week {week_number} of {year}-{year+1}",
        }
        return render(request, 'agency/weekly_timesheets.html', context)

    def generate_monthly_report(self, request):
        year = request.POST.get('year')
        month_number = request.POST.get('month_number')
        care_home_name = request.POST.get('care_home_name')

        if not year or not month_number or not care_home_name:
            return HttpResponseBadRequest('Year, month number, and care home name are required.')

        try:
            year = int(year)
            month_number = int(month_number)
        except ValueError:
            return HttpResponseBadRequest('Invalid year or month number.')

        # Fetch timesheets for the selected month and care home
        try:
            start_date = datetime(year, month_number, 1)
            _, last_day = calendar.monthrange(year, month_number)
            end_date = datetime(year, month_number, last_day)
        except ValueError:
            return HttpResponseBadRequest('Invalid month number or year.')

        timesheets = TimeSheet.objects.filter(
            date_of_work__gte=start_date,
            date_of_work__lte=end_date,
            care_home_name=care_home_name  # Adjust this filter based on your CareHome model fields
        ).order_by('user', 'date_of_work')

        # Calculate total worked hours for each timesheet entry
        timesheets = timesheets.annotate(
            total_worked_hours=ExpressionWrapper(
                F('shift_finished_time') - F('shift_started_time'),
                output_field=DurationField()
            )
        )

        context = {
            'timesheets': timesheets,
            'month_range': f"{calendar.month_name[month_number]} {year}",
        }
        return render(request, 'agency/monthly_timesheets.html', context)

class WeeklyTimesheetsView(View):
    template_name = 'agency/weekly_timesheets.html'

    def get(self, request):
        week_number = request.GET.get('week_number')
        year = request.GET.get('year')
        staff_name = request.GET.get('staff_name')

        if not week_number or not year or not staff_name:
            return HttpResponseBadRequest('Week number, year, and staff name are required.')

        try:
            week_number = int(week_number)
            year = int(year)
        except ValueError:
            return HttpResponseBadRequest('Invalid week number or year.')

        # Query the timesheets for the selected week and staff
        timesheets = TimeSheet.objects.filter(
            date_of_work__week=week_number,
            date_of_work__year=year,
            user__first_name=staff_name
        ).order_by('care_home_name', 'date_of_work')

        # Calculate total worked hours for each timesheet entry
        timesheets = timesheets.annotate(
            total_worked_hours=ExpressionWrapper(
                F('shift_finished_time') - F('shift_started_time'),
                output_field=DurationField()
            )
        )

        context = {
            'timesheets': timesheets,
            'week_number': week_number,
            'year': year,
            'staff_name': staff_name,
        }

        return render(request, self.template_name, context)


class MonthlyTimesheetsView(View):
    template_name = 'agency/monthly_timesheets.html'

    def get(self, request):
        month_number = request.GET.get('month_number')
        year = request.GET.get('year')
        care_home_name = request.GET.get('client_username')

        if not month_number or not year or not care_home_name:
            return HttpResponseBadRequest('Month number, year, and care home name are required.')

        try:
            month_number = int(month_number)
            year = int(year)
        except ValueError:
            return HttpResponseBadRequest('Invalid month number or year.')

        # Query the timesheets for the selected month and care home
        timesheets = TimeSheet.objects.filter(
            date_of_work__month=month_number,
            date_of_work__year=year,
            care_home_id__username=care_home_name  # Adjust this filter based on your CareHome model fields
        ).order_by('user', 'date_of_work')

        # Calculate total worked hours for each timesheet entry
        timesheets = timesheets.annotate(
            total_worked_hours=ExpressionWrapper(
                F('shift_finished_time') - F('shift_started_time'),
                output_field=DurationField()
            )
        )

        context = {
            'timesheets': timesheets,
            'month_number': month_number,
            'year': year,
            'care_home_name': care_home_name,
        }

        return render(request, self.template_name, context)
