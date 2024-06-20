from django.urls import path
from . import views


urlpatterns = [
    path("staffloginpage/", views.stafflogin, name='staff-login'),
    path("stafffrontpage/", views.staff_front, name='staff-front'),
    path('staffloginpage/changepassword/', views.change_password, name='change-password'),
    path('stafffrontpage/timesheet/', views.submit_timesheet, name='submit-timesheet'),
    path('timesheet/success_timesheet/', views.success_page, name='success-page'), 
    path('timesheets/<int:year>/<int:week_number>/', views.retrieve_timesheets_for_week, name='retrieve-timesheets-for-week'),
    path('create-weeks/<int:year>/', views.create_weeks_table_view, name='create-weeks'),
    path('create_weeks/success_weekcreation/', views.success_weekcreation, name='success_weekcreation'), 


]
