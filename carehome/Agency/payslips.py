from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
from staff.models import WeekDateRange
from .models import CustomUser
from datetime import datetime


def prepare_context():
    current_year = datetime.now().year
    years = range(2024, current_year + 1)
    week_date_ranges = WeekDateRange.objects.all()
    staff_names = CustomUser.objects.filter(groups__name='staff')
    context = {
        'years': years,
        'week_date_ranges': week_date_ranges,
        'staff_names': staff_names,
    }
    return context

def get_weekly_view(request):
    context = prepare_context()
    return render(request, 'agency/upload_payslip.html', context)

def upload_payslip(request):
    if request.method == 'POST':
        year = request.POST.get('year')
        week_number = request.POST.get('week_number')
        staff_id = request.POST.get('staff_name')
        file = request.FILES['file']
        
        staff = CustomUser.objects.get(id=staff_id)
        week = WeekDateRange.objects.get(year=year, week_number=week_number)

        # Create directory path for payslips within generated_reports
        directory_path = os.path.join(settings.GENERATED_REPORTS_DIR, 'payslips', str(year), week.week_name)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        # Save file
        file_name = f"{staff.first_name}_{staff.last_name}_{week.week_name}.pdf"
        file_path = os.path.join(directory_path, file_name)
        fs = FileSystemStorage(location=directory_path)
        fs.save(file_name, file)

        success_message = f"File uploaded successfully for {staff.first_name} {staff.last_name} for {week.week_name}"

        context = prepare_context()
        context['success_message'] = success_message

        return render(request, 'agency/upload_payslip.html', context)

    return get_weekly_view(request)