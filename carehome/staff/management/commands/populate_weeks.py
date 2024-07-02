from django.utils.timezone import make_aware
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from staff.models import WeekDateRange


def get_start_of_week(date):
    """
    Given a date, return the Monday of that week.
    """
    start_of_week = date - timedelta(days=date.weekday())
    return start_of_week

def get_week1_start(year):
    """
    Get the Monday of the week that includes April 1st for a given year.
    """
    april_first = datetime(year, 4, 1)
    return get_start_of_week(april_first)

def get_week_date_range(year, week_number):
    """
    Get the date range (Monday to Sunday) for the given week number starting from week1.
    """
    week1_start = get_week1_start(year)
    start_of_week = week1_start + timedelta(weeks=week_number - 1)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def generate_weeks_table(start_year, end_year):
    """
    Generate a table of weeks from 'Week 1 of start_year-end_year' to the last week of March end_year with their date ranges.
    """
    weeks_table = []
    current_year = start_year
    week_number = 1

    while current_year <= end_year:
        start_of_week, end_of_week = get_week_date_range(current_year, week_number)
        if start_of_week.month == 4 and week_number == 1:
            week_name = f"Week 1 of {current_year}-{current_year+1}"
        else:
            week_name = f"Week {week_number}"
        
        weeks_table.append({
            'year': current_year,
            'week_number': week_number,
            'week_name': week_name,
            'start_date': start_of_week,
            'end_date': end_of_week
        })
        
        week_number += 1
        if start_of_week.month == 3 and start_of_week.day >= 25:
            week_number = 1
            current_year += 1

    return weeks_table

class Command(BaseCommand):
    help = 'Populate the WeekDateRange table with weeks and their date ranges for the specified years'

    def add_arguments(self, parser):
        parser.add_argument('start_year', type=int, help='Start year for week date range')
        parser.add_argument('end_year', type=int, help='End year for week date range')

    def handle(self, *args, **kwargs):
        start_year = kwargs['start_year']
        end_year = kwargs['end_year']
        
        weeks_table = generate_weeks_table(start_year, end_year)
        
        for week in weeks_table:
            WeekDateRange.objects.update_or_create(
                year=week['year'],
                week_number=week['week_number'],
                defaults={
                    'week_name': week['week_name'],
                    'start_date': make_aware(week['start_date']),
                    'end_date': make_aware(week['end_date'])
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully populated WeekDateRange table for {start_year}-{end_year}'))

