# models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    needs_password_change = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, related_name='customuser_set')
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set_permissions')


class StaffPreference(models.Model):
    care_home_name = models.CharField(max_length=100)
    date = models.DateField()
    week_name = models.CharField(max_length=100)
    staff_required_field = models.CharField(max_length=50)
    staff_name = models.CharField(max_length=100)
    staff_required_sum = models.IntegerField(default=0)  # New field to store the sum

    def __str__(self):
        return f"{self.care_home_name} - {self.date} - {self.staff_name} - {self.staff_required_field}"