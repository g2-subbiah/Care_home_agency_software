from .models import TimeSheet
import pandas as pd
from django.db.models import Q
from django.utils.timezone import make_aware
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from staff.models import TimeSheet, WeekDateRange

class Command(BaseCommand):
    help = 'Fetch TimeSheet entries for a specific week and convert to pandas DataFrame'

    def handle(self, *args, **kwargs):
        # Define the year and week number you are interested in
        year = 2024  # Example: Replace with the year you are interested in
        week_number = 1  # Example: Replace with the week number you are interested in

        try:
            # Query the WeekDateRange object for the specified year and week number
            week_range = WeekDateRange.objects.get(year=year, week_number=week_number)

            # Get the start_date and end_date for the specified WeekDateRange
            start_date = week_range.start_date
            end_date = week_range.end_date

            # Filter TimeSheet entries for the specified week
            timesheets = TimeSheet.objects.filter(
                Q(date_of_work__gte=start_date) &
                Q(date_of_work__lte=end_date)
            )

            # Convert queryset to pandas DataFrame
            timesheets_data = list(timesheets.values())  # Convert queryset to list of dictionaries
            df = pd.DataFrame(timesheets_data)

            # Print or process the DataFrame as needed
            print(df)

            # Optionally, return the DataFrame or perform other operations
            return df

        except WeekDateRange.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'WeekDateRange not found for year {year} and week {week_number}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to fetch TimeSheet entries: {str(e)}'))
