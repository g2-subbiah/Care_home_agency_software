from django.core.management.base import BaseCommand
from staff.models import WeekDateRange
from client.models import DateInfo
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate DateInfo table for all weeks in WeekDateRange'

    def handle(self, *args, **kwargs):
        weeks = WeekDateRange.objects.all()
        for week in weeks:
            current_date = week.start_date
            while current_date <= week.end_date:
                DateInfo.objects.get_or_create(
                    date=current_date,
                    weekday=current_date.strftime('%A'),
                    week=week
                )
                current_date += timedelta(days=1)
        self.stdout.write(self.style.SUCCESS('Successfully populated DateInfo table.'))
