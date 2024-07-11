from django.shortcuts import render
from staff.models import Week_2
from client.models import Week
from django.utils import timezone
from datetime import date 


def match_staff(request):
    context = {}

    current_date = date.today()

    # Fetch all weeks from the Week model starting from today's date
    weeks = Week.objects.filter(date__gte=current_date).order_by('week_name', 'date')

    # Extract unique week names and years
    week_names = sorted(set(weeks.values_list('week_name', flat=True)))
    week_years = sorted(set(weeks.values_list('date__year', flat=True)))

    context = {
        'week_names': week_names,  # For the dropdown
        'week_years': week_years,  # For the year input
        'current_date': current_date,
    }

    if request.method == 'POST':
        week_name = request.POST.get('week_name')
        year = request.POST.get('year')

        # Fetch data from Week model for selected week_name and year
        week_data = Week.objects.filter(week_name=week_name, date__year=year).order_by('care_home_name', 'date')

        # Fetch data from Week_2 model for selected week_name and year
        week_2_data = Week_2.objects.filter(week_name=week_name, date__year=year).order_by('week_day', 'staff_name')

        organized_data = {}
        staff_availability = {}

        for week in week_data:
            care_home_name = week.care_home_name
            week_date = week.date
            if care_home_name not in organized_data:
                organized_data[care_home_name] = {
                    'week_name': week.week_name,
                    'data': {},
                }
            
            if week_date not in organized_data[care_home_name]['data']:
                organized_data[care_home_name]['data'][week_date] = {
                    'staff_required_sum': 0,
                    'staff_required': {
                        'staff_required_1': 0,
                        'staff_required_2': 0,
                        'staff_required_3': 0,
                        'staff_required_4': 0,
                    },
                    'staff_availability': {
                        'staff_required_1': [],
                        'staff_required_2': [],
                        'staff_required_3': [],
                        'staff_required_4': [],
                    }
                }

            # Calculate sum of staff_required_x fields for the date
            for i in range(1, 5):
                staff_field = f'staff_required_{i}'
                staff_count = getattr(week, staff_field, 0)
                organized_data[care_home_name]['data'][week_date]['staff_required'][staff_field] += staff_count
                organized_data[care_home_name]['data'][week_date]['staff_required_sum'] += staff_count

                # Check if staff_required_x is greater than 0 for the date
                if staff_count > 0:
                    # Determine the corresponding availability field based on staff_required_x
                    if i == 1:
                        availability_field = 'staff_availability_1'
                    elif i == 2:
                        availability_field = 'staff_availability_2'
                    elif i == 3:
                        availability_field = 'staff_availability_1'  # Adjust as per your actual logic
                    elif i == 4:
                        availability_field = 'staff_availability_1'  # Adjust as per your actual logic

                    availability = list(week_2_data.filter(date=week_date, **{availability_field: True}).values_list('staff_name', flat=True))
                    organized_data[care_home_name]['data'][week_date]['staff_availability'][staff_field] = availability
        
        context.update({
            'organized_data': organized_data,
            'selected_week_name': week_name,
            'current_date': current_date,
        })

    return render(request, 'agency/allotments.html', context)