from django.shortcuts import render, redirect
from staff.models import Week_2
from client.models import Week
from .models import StaffPreference
from .forms import StaffPreferenceForm
from django.utils import timezone
from datetime import date, datetime
from django.contrib import messages
from django.http import JsonResponse


def match_staff(request):
    context = {}
    current_date = date.today()
    weeks = Week.objects.filter(date__gte=current_date).order_by('week_name', 'date')
    week_names = sorted(set(weeks.values_list('week_name', flat=True)))
    week_years = sorted(set(weeks.values_list('date__year', flat=True)))

    context = {
        'week_names': week_names,
        'week_years': week_years,
        'current_date': current_date,
    }

    if request.method == 'POST':
        week_name = request.POST.get('week_name')
        year = request.POST.get('year')


        week_data = Week.objects.filter(week_name=week_name, date__year=year).exclude(date__isnull=True).order_by('care_home_name', 'date')
        
        if not week_data.exists():
            messages.error(request, 'No data found for the selected week and year.')
            return redirect('allotments')  
        week_2_data = Week_2.objects.filter(week_name=week_name, date__year=year).order_by('week_day', 'staff_name')

        organized_data = organize_data(week_data, week_2_data)

        preferences_saved_dates = []
        for week in week_data:
            if StaffPreference.objects.filter(care_home_name=week.care_home_name, date=week.date).exists():
                preferences_saved_dates.append(week.date)

        context.update({
            'organized_data': organized_data,
            'selected_week_name': week_name,
            'preferences_saved_dates': preferences_saved_dates,  # Pass the list of saved dates
            'year':year
        })

    return render(request, 'agency/allotments.html', context)

def organize_data(week_data, week_2_data):
    organized_data = {}

    for week in week_data:
        care_home_name = week.care_home_name
        week_date = week.date

        if care_home_name not in organized_data:
            organized_data[care_home_name] = {'week_name': week.week_name, 'data': {}}

        if week_date not in organized_data[care_home_name]['data']:
            organized_data[care_home_name]['data'][week_date] = {
                'staff_required_sum': 0,
                'staff_required': {'staff_required_1': 0, 'staff_required_2': 0, 'staff_required_3': 0, 'staff_required_4': 0},
                'staff_availability': {'staff_required_1': [], 'staff_required_2': [], 'staff_required_3': [], 'staff_required_4': []}
            }

        for i in range(1, 5):
            staff_field = f'staff_required_{i}'
            staff_count = getattr(week, staff_field, 0)
            organized_data[care_home_name]['data'][week_date]['staff_required'][staff_field] += staff_count
            organized_data[care_home_name]['data'][week_date]['staff_required_sum'] += staff_count

            if staff_count > 0:
                if i > 2:
                    availability_field = 'staff_availability_1'
                else:
                    availability_field = f'staff_availability_{i}'
                
                availability = list(week_2_data.filter(date=week_date, **{availability_field: True}).values_list('staff_name', flat=True))
                organized_data[care_home_name]['data'][week_date]['staff_availability'][staff_field] = availability
    
    return organized_data

def save_preferences_logic(request):
    if request.method == 'POST':
        care_home_name = request.POST.get('care_home_name')
        date_value = request.POST.get('date')
        week_name = request.POST.get('week_name')

        try:
            date_value = datetime.strptime(date_value, "%B %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Please use YYYY-MM-DD format.'}, status=400)

        selected_staff = {
            'staff_required_1': request.POST.getlist('staff_required_1'),
            'staff_required_2': request.POST.getlist('staff_required_2'),
            'staff_required_3': request.POST.getlist('staff_required_3'),
            'staff_required_4': request.POST.getlist('staff_required_4')
        }

        week_data = Week.objects.filter(care_home_name=care_home_name, date=date_value).first()
        if not week_data:
            return JsonResponse({'error': 'Week data not found.'}, status=404)

        errors = validate_staff_selection(selected_staff, week_data)
        if errors:
            return JsonResponse({'error': errors}, status=400)

        save_staff_preferences(care_home_name, date_value, week_name, selected_staff, week_data)

        return JsonResponse({'success': f'Preferences for {date_value} saved for {care_home_name} successfully.'})

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def validate_staff_selection(selected_staff, week_data):
    errors = []

    time_zone_staff = {
        'staff_required_1': [],
        'staff_required_3': [],
        'staff_required_4': [],
        'staff_required_2': []
    }

    for key in selected_staff:
        for staff in selected_staff[key]:
            if staff in time_zone_staff['staff_required_1'] + time_zone_staff['staff_required_3'] + time_zone_staff['staff_required_4']:
                errors.append(f'Staff {staff} cannot be assigned to overlapping time zones.')
            time_zone_staff[key].append(staff)

    for i in range(1, 5):
        staff_field = f'staff_required_{i}'
        if len(selected_staff[staff_field]) > getattr(week_data, staff_field):
            errors.append(f'The number of staff selected for {staff_field.replace("_", " ").title()} exceeds the required number.')
    return errors


def save_staff_preferences(care_home_name, date_value, week_name, selected_staff, week_data):
    for i in range(1, 5):
        staff_field = f'staff_required_{i}'
        selected_count = len(selected_staff[staff_field])  # Count of selected staff for this specific field

        for staff in selected_staff[staff_field]:
            # Check if a preference already exists based on the first four fields
            preference, created = StaffPreference.objects.update_or_create(
                care_home_name=care_home_name,
                date=date_value,
                week_name=week_name,
                staff_required_field=staff_field,
                defaults={
                    'staff_name': staff,
                    'staff_required_sum': selected_count
                }
            )



