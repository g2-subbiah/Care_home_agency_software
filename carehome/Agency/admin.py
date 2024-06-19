# admin.py in the Agency app

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('needs_password_change',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
