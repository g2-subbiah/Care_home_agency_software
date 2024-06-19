from django.urls import path
from . import views

urlpatterns = [
    path("staffloginpage/", views.stafflogin, name='staff-login'),
    path("stafffrontpage/", views.staff_front, name='staff-front'),
    path("stafffrontpage/timesheet/", views.timesheet, name='timesheet'),
    path('staffloginpage/changepassword/', views.change_password, name='change-password'),

]
