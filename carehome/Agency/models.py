# models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    needs_password_change = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, related_name='customuser_set')
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set_permissions')


# Create your models here.
# class User(models.Model):
#     username = models.CharField(max_length=150, unique=True)
#     password = models.CharField(max_length=128)  # Storing hashed passwords is recommended

#     def __str__(self):
#         return self.username

