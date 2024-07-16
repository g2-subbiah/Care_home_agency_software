from django.shortcuts import render
from .models import StaffPreference
from client.models import Week
from django.db.models.functions import ExtractYear

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
        organized_dates = [date.strftime('%Y-%m-%d') for date in organized_data[care_home_name]['data'].keys()]


        print("Organized_dates:", organized_dates)

        # Collect staff data for the pop-up
        staff_data = StaffPreference.objects.filter(
            date__in=organized_dates,
            care_home_name=care_home_name
        ).values('date', 'staff_required_field', 'staff_name')

        formatted_staff_data = []
        for entry in staff_data:
            formatted_entry = {
                'date': entry['date'].strftime('%Y-%m-%d'),  # Convert to string format
                'staff_required_field': entry['staff_required_field'],
                'staff_name': entry['staff_name'],
            }
            formatted_staff_data.append(formatted_entry)

        print("Staff Data:", list(formatted_staff_data))  # Convert to list for easier reading

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
            date = entry['date']  # Ensure you get the date from the entry
            if date in grouped_staff and field in grouped_staff[date]:
                grouped_staff[date][field].append(name)

        print("Grouped Staff:", grouped_staff)


        context = {
            'care_home_name': care_home_name,
            'selected_week_name': week_name,
            'year': year,
            'data': organized_data.get(care_home_name, {}).get('data', {}),
            'staff_data': grouped_staff,  # Pass the grouped staff data to the template
        }
        return render(request, 'agency/client_schedule.html', context)

    context = {
        'years': years,
        'week_names': week_names,
        'care_home_names': care_home_names,
    }
    return render(request, 'agency/schedule_page1.html', context)
