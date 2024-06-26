import os
import calendar
from datetime import datetime, timedelta
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views import View
from django.template.loader import render_to_string
from staff.models import TimeSheet
import matplotlib.pyplot as plt

class TimesheetView(View):
    template_name = 'agency/timesheets_view.html'

    def get(self, request):
        current_year = datetime.now().year
        years = [current_year]
        months = {i: calendar.month_name[i] for i in range(1, 13)}
        week_date_ranges = self.get_week_date_ranges(current_year)

        context = {
            'years': years,
            'months': months,
            'week_date_ranges': week_date_ranges,
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
        week_date_ranges = []
        for week_number in range(1, 53):
            start_date, end_date = self.get_week_date_range(year, week_number)
            week_date_ranges.append({
                'year': year,
                'week_number': week_number,
                'start_date': start_date,
                'end_date': end_date,
            })
        return week_date_ranges

    def get_week_date_range(self, year, week_number):
        start_date = datetime(year, 1, 1) + timedelta(days=(week_number - 1) * 7)
        end_date = start_date + timedelta(days=6)
        return start_date, end_date

    def get_month_date_range(self, year, month):
        start_date = datetime(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = datetime(year, month, last_day)
        return start_date, end_date

    def generate_weekly_report(self, request):
        year = int(request.POST.get('year'))
        week_number = int(request.POST.get('week_number'))

        start_date, end_date = self.get_week_date_range(year, week_number)
        timesheets = TimeSheet.objects.filter(
            date_of_work__gte=start_date,
            date_of_work__lte=end_date
        ).order_by('care_home_name', 'date_of_work')

        plt.figure(figsize=(10, 6))
        plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
        plt.title('Weekly Timesheet Report')
        plt.xlabel('X-axis label')
        plt.ylabel('Y-axis label')

        # Generate a unique filename for the report
        report_filename = f'weekly_timesheet_report_{year}_week_{week_number}.png'
        report_path = os.path.join(settings.GENERATED_REPORTS_DIR, report_filename)
        plt.savefig(report_path)
        plt.close()

        report_url = os.path.join('/generated_reports', report_filename)
        request.session['report_url'] = report_url
        return redirect('weekly_timesheets_view')

    def generate_monthly_report(self, request):
        year = int(request.POST.get('year'))
        month_number = int(request.POST.get('month_number'))

        start_date, end_date = self.get_month_date_range(year, month_number)
        timesheets = TimeSheet.objects.filter(
            date_of_work__gte=start_date,
            date_of_work__lte=end_date
        ).order_by('care_home_name', 'date_of_work')

        plt.figure(figsize=(10, 6))
        plt.plot([1, 2, 3, 4], [1, 8, 27, 64])
        plt.title('Monthly Timesheet Report')
        plt.xlabel('X-axis label')
        plt.ylabel('Y-axis label')

        # Generate a unique filename for the report
        report_filename = f'monthly_timesheet_report_{year}_{month_number}.png'
        report_path = os.path.join(settings.GENERATED_REPORTS_DIR, report_filename)
        plt.savefig(report_path)
        plt.close()

        report_url = os.path.join('/generated_reports', report_filename)
        request.session['report_url'] = report_url
        return redirect('monthly_timesheets_view')

def weekly_timesheets_view(request):
    report_url = request.session.get('report_url')
    context = {'report_url': report_url}
    return render(request, 'agency/weekly_timesheets.html', context)

def monthly_timesheets_view(request):
    report_url = request.session.get('report_url')
    context = {'report_url': report_url}
    return render(request, 'agency/monthly_timesheets.html', context)
