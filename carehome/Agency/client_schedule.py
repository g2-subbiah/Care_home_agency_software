from django.shortcuts import render
from .models import StaffPreference
from client.models import Week
from django.db.models.functions import ExtractYear
from .models import CustomUser
from django.contrib.auth.decorators import login_required
from staff.models import WeekDateRange
from django.utils import timezone


def organize_data(week_data):
    organized_data = {}

    for week in week_data:
        care_home_name = week.care_home_name
        week_date = week.date

        if care_home_name not in organized_data:
            organized_data[care_home_name] = {
                'week_name': week.week_name,
                'data': {}
            }

        if week_date not in organized_data[care_home_name]['data']:
            organized_data[care_home_name]['data'][week_date] = {
                'staff_required': {
                    'staff_required_1': week.staff_required_1,
                    'staff_required_2': week.staff_required_2,
                    'staff_required_3': week.staff_required_3,
                    'staff_required_4': week.staff_required_4,
                },
                'staff_availability': {
                    'staff_required_1': [],
                    'staff_required_2': [],
                    'staff_required_3': [],
                    'staff_required_4': [],
                }
            }

    return organized_data


def schedule_view(request):
    years = Week.objects.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct()
    week_names = Week.objects.values_list('week_name', flat=True).distinct()
    care_home_names = Week.objects.values_list('care_home_name', flat=True).distinct()

    if request.method == 'POST':
        year = request.POST.get('year')
        week_name = request.POST.get('week_name')
        care_home_name = request.POST.get('care_home_name')

        week_data = Week.objects.filter(
            date__year=year,
            week_name=week_name,
            care_home_name=care_home_name
        )

        organized_data = organize_data(week_data)
        organized_dates = [date for date in organized_data[care_home_name]['data'].keys()]

        # Format dates to 'Y-m-d'
        formatted_dates = [date.strftime('%Y-%m-%d') for date in organized_dates]

        # Collect staff data for the pop-up
        staff_data = StaffPreference.objects.filter(
            date__in=formatted_dates,  # Use formatted dates here
            care_home_name=care_home_name
        ).values('date', 'staff_required_field', 'staff_name')

        formatted_staff_data = []
        for entry in staff_data:
            formatted_entry = {
                'date': entry['date'],  # Keep the original date format if needed
                'staff_required_field': entry['staff_required_field'],
                'staff_name': entry['staff_name'],
            }
            formatted_staff_data.append(formatted_entry)

        # Grouping staff names by their required field
        grouped_staff = {
            date: {
                'staff_required_1': [],
                'staff_required_2': [],
                'staff_required_3': [],
                'staff_required_4': []
            }
            for date in organized_data[care_home_name]['data'].keys()
        }

        for entry in formatted_staff_data:
            field = entry['staff_required_field']
            name = entry['staff_name']
            date = entry['date']
            if date in grouped_staff and field in grouped_staff[date]:
                grouped_staff[date][field].append(name)

        context = {
            'care_home_name': care_home_name,
            'selected_week_name': week_name,
            'year': year,
            'data': organized_data.get(care_home_name, {}).get('data', {}),
            'staff_data': grouped_staff,
        }
        return render(request, 'agency/client_schedule.html', context)

    context = {
        'years': years,
        'week_names': week_names,
        'care_home_names': care_home_names,
    }
    return render(request, 'agency/schedule_page1.html', context)


@login_required
def client_schedule_view(request):
    care_home_name = request.user.first_name
    current_date = timezone.now().date()

    # Fetch the current year and week based on the current date
    current_week_range = WeekDateRange.objects.filter(start_date__lte=current_date, end_date__gte=current_date).first()
    
    if current_week_range:
        default_year = current_week_range.year
        default_week_name = current_week_range.week_name
    else:
        default_year = None  # Handle the case if no current week is found
        default_week_name = None

    years = Week.objects.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct()
    week_names = Week.objects.values_list('week_name', flat=True).distinct()

    if request.method == 'POST':
        year = request.POST.get('year', default_year)
        week_name = request.POST.get('week_name', default_week_name)
    else:
        year = default_year
        week_name = default_week_name

    week_data = Week.objects.filter(
        date__year=year,
        week_name=week_name,
        care_home_name=care_home_name
    )

    organized_data = organize_data(week_data)

    # Check if care_home_name exists in organized_data
    if care_home_name in organized_data:
        organized_dates = [date for date in organized_data[care_home_name]['data'].keys()]
        formatted_dates = [date.strftime('%Y-%m-%d') for date in organized_dates]

        staff_data = StaffPreference.objects.filter(
            date__in=formatted_dates,
            care_home_name=care_home_name
        ).values('date', 'staff_required_field', 'staff_name')

        formatted_staff_data = []
        for entry in staff_data:
            formatted_entry = {
                'date': entry['date'],
                'staff_required_field': entry['staff_required_field'],
                'staff_name': entry['staff_name'],
            }
            formatted_staff_data.append(formatted_entry)

        grouped_staff = {
            date: {
                'staff_required_1': [],
                'staff_required_2': [],
                'staff_required_3': [],
                'staff_required_4': []
            }
            for date in organized_data[care_home_name]['data'].keys()
        }

        for entry in formatted_staff_data:
            field = entry['staff_required_field']
            name = entry['staff_name']
            date = entry['date']
            if date in grouped_staff and field in grouped_staff[date]:
                grouped_staff[date][field].append(name)

    else:
        organized_data = {care_home_name: {'data': {}}}
        grouped_staff = {}

    # Check if there are entries in the StaffPreference table for the selected week_name and care_home_name
    schedule_exists = StaffPreference.objects.filter(
        week_name=week_name,
        care_home_name=care_home_name
    ).exists()

    context = {
        'care_home_name': care_home_name,
        'selected_week_name': week_name,
        'default_year': default_year,
        'default_week_name': default_week_name,
        'year': year,
        'years': years,
        'week_names': week_names,
        'data': organized_data.get(care_home_name, {}).get('data', {}),
        'staff_data': grouped_staff,
        'schedule_exists': schedule_exists,  # Add this to the context
    }
    return render(request, 'client/scheduling_client.html', context)

