# models.py
# from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from staff.models import WeekDateRange

# class CustomUser(AbstractUser):
#     needs_password_change = models.BooleanField(default=True)
#     groups = models.ManyToManyField(Group, related_name='customuser_set')
#     user_permissions = models.ManyToManyField(Permission, related_name='customuser_set_permissions')


class Week(models.Model):
    date = models.DateField()
    week_name = models.CharField(max_length=100)
    week_day = models.CharField(max_length=100)
    care_home_name = models.CharField(max_length=100)
    staff_required_1 = models.IntegerField()
    staff_required_2 = models.IntegerField()
    staff_required_3 = models.IntegerField()
    staff_required_4 = models.IntegerField()



    def __str__(self):
        return f"{self.week_name} - {self.date}"
    
class DateInfo(models.Model):
    date = models.DateField()
    weekday = models.CharField(max_length=20)
    week = models.ForeignKey(WeekDateRange, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date} ({self.weekday})"