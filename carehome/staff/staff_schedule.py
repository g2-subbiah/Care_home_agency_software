from django.shortcuts import render
from Agency.models import StaffPreference
from staff.models import Week_2
from django.db.models.functions import ExtractYear
from django.contrib.auth.decorators import login_required
from staff.models import WeekDateRange
from django.utils import timezone

def organize_data(week_data, staff_data):
    organized_data = {}

    for week in week_data:
        staff_name = week.staff_name
        week_date = week.date

        if staff_name not in organized_data:
            organized_data[staff_name] = {
                'week_name': week.week_name,
                'data': {}
            }

        if week_date not in organized_data[staff_name]['data']:
            organized_data[staff_name]['data'][week_date] = {
                'staff_required': {
                    'staff_required_1': [],
                    'staff_required_2': [],
                    'staff_required_3': [],
                    'staff_required_4': [],
                },
                'staff_availability': {
                    'staff_availability_1': week.staff_availability_1,
                    'staff_availability_2': week.staff_availability_2,
                }
            }

    for entry in staff_data:
        date = entry['date']
        field = entry['staff_required_field']
        care_home_name = entry['care_home_name']
        staff_name = entry['staff_name']

        if staff_name in organized_data and date in organized_data[staff_name]['data']:
            organized_data[staff_name]['data'][date]['staff_required'][field].append(care_home_name)

    return organized_data


def availability_view(request):
    years = Week_2.objects.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct()
    week_names = Week_2.objects.values_list('week_name', flat=True).distinct()
    staff_names = Week_2.objects.values_list('staff_name', flat=True).distinct()

    if request.method == 'POST':
        year = request.POST.get('year')
        week_name = request.POST.get('week_name')
        staff_name = request.POST.get('staff_name')

        week_data = Week_2.objects.filter(
            date__year=year,
            week_name=week_name,
            staff_name=staff_name
        )

        staff_data = StaffPreference.objects.filter(
            date__year=year,
            staff_name=staff_name
        ).values('date', 'staff_required_field', 'care_home_name', 'staff_name')

        organized_data = organize_data(week_data, staff_data)

        context = {
            'staff_name': staff_name,
            'selected_week_name': week_name,
            'year': year,
            'data': organized_data.get(staff_name, {}).get('data', {}),
        }
        return render(request, 'agency/staff_schedule.html', context)

    context = {
        'years': years,
        'week_names': week_names,
        'staff_names': staff_names,
    }
    return render(request, 'agency/schedule_page2.html', context)


@login_required
def staff_availability_view(request):
    staff_name = f"{request.user.first_name} {request.user.last_name}"
    current_date = timezone.now().date()

    current_week_range = WeekDateRange.objects.filter(start_date__lte=current_date, end_date__gte=current_date).first()
    
    if current_week_range:
        default_year = current_week_range.year
        default_week_name = current_week_range.week_name
    else:
        default_year = None
        default_week_name = None

    years = Week_2.objects.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct()
    week_names = Week_2.objects.values_list('week_name', flat=True).distinct()

    if request.method == 'POST':
        year = request.POST.get('year', default_year)
        week_name = request.POST.get('week_name', default_week_name)
    else:
        year = default_year
        week_name = default_week_name

    # Fetch week data
    week_data = Week_2.objects.filter(
        date__year=year,
        week_name=week_name,
        staff_name=staff_name
    )

    # Fetch staff data and organize it
    staff_data = StaffPreference.objects.filter(
        date__year=year,
        week_name=week_name,
        staff_name=staff_name
    ).values('date', 'staff_required_field', 'care_home_name', 'staff_name')

    organized_data = organize_data(week_data, staff_data)
    

    context = {
        'staff_name': staff_name,
        'selected_week_name': week_name,
        'default_year': default_year,
        'default_week_name': default_week_name,
        'year': year,
        'years': years,
        'week_names': week_names,
        'data': organized_data.get(staff_name, {}).get('data', {}),
    }
    
    return render(request, 'staff/scheduling_staff.html', context)
