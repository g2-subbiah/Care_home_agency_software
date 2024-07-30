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

from django.db import models

class PersonalDetails(models.Model):
    # Existing fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15)
    email_id = models.EmailField()
    address = models.TextField()
    emergency_contact_number = models.CharField(max_length=15)
    ni_number = models.CharField(max_length=20)
    
    # New field to track status
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class DocumentsCollection(models.Model):
    personal_details = models.OneToOneField(PersonalDetails, on_delete=models.CASCADE, related_name='documents')
    passport_number = models.CharField(max_length=50)
    passport_date = models.DateField()
    passport_expiry_date = models.DateField()
    brp_number = models.CharField(max_length=50)
    brp_date = models.DateField()
    brp_expiry_date = models.DateField()
    training_number = models.CharField(max_length=50)
    training_date = models.DateField()
    training_expiry_date = models.DateField()
    dbs_number = models.CharField(max_length=50)
    dbs_date = models.DateField()
    dbs_expiry_date = models.DateField()

    def __str__(self):
        return f"Documents for {self.personal_details.first_name} {self.personal_details.last_name}"
