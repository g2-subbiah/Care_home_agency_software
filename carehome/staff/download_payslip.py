from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, FileResponse
import os
from Agency.models import CustomUser
from .models import WeekDateRange
from datetime import datetime

def prepare_download_context(user):
    current_year = datetime.now().year
    years = range(2024, current_year + 1)
    week_date_ranges = WeekDateRange.objects.all()
    context = {
        'years': years,
        'week_date_ranges': week_date_ranges,
        'user': user,
    }
    return context

def download_payslip(request):
    user = request.user
    if not user.is_authenticated or not user.groups.filter(name='staff').exists():
        return redirect('login')  # Adjust 'login' to your login URL name

    if request.method == 'POST':
        year = request.POST.get('year')
        week_number = request.POST.get('week_number')
        
        week = get_object_or_404(WeekDateRange, year=year, week_number=week_number)

        # Construct file path
        file_name = f"{user.first_name}_{user.last_name}_{week.week_name}.pdf"
        directory_path = os.path.join(settings.GENERATED_REPORTS_DIR, 'payslips', str(year), week.week_name)
        file_path = os.path.join(directory_path, file_name)

        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), as_attachment=True)
            return response
        else:
            context = prepare_download_context(user)
            context['error_message'] = "Payslip not found for the selected week and year."
            return render(request, 'staff/download_payslip.html', context)

    context = prepare_download_context(user)
    return render(request, 'staff/download_payslip.html', context)
