# models.py

from django.db import models
from django.conf import settings

class TimeSheet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    staff_name = models.CharField(max_length=100)  
    care_home_id = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='timesheets', on_delete=models.CASCADE)
    care_home_name = models.CharField(max_length=100)
    date_of_work = models.DateField()
    shift_started_time = models.DateTimeField()
    break_started_time = models.TimeField()
    break_finished_time = models.TimeField()
    shift_finished_time = models.DateTimeField()
    client_rep_name = models.CharField(max_length=100)
    client_rep_position = models.CharField(max_length=100)
    staff_signature_image = models.ImageField(upload_to='staff_signatures/', null=True, blank=True)
    client_rep_signature_image = models.ImageField(upload_to='client_rep_signatures/', null=True, blank=True)
    
    def __str__(self):
        return f"TimeSheet for {self.staff_name} on {self.date_of_work}"
    
class WeekDateRange(models.Model):
    year = models.IntegerField()
    week_number = models.IntegerField()
    week_name = models.CharField(max_length=50, default='')  
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        # return f"Week {self.week_number} of {self.year}: {self.start_date} - {self.end_date}"
        return f"{self.week_name}: {self.start_date} - {self.end_date}"
    
class Week_2(models.Model):
    date = models.DateField()
    week_name = models.CharField(max_length=100)
    week_day = models.CharField(max_length=100)
    staff_name = models.CharField(max_length=100)
    staff_availability_1 = models.BooleanField()
    staff_availability_2 = models.BooleanField()

    def __str__(self):
        return f"{self.week_name} - {self.date}"
