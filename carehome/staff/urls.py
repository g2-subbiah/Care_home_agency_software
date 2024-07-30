from django.urls import path
from . import views
from .views import FileUploadView

urlpatterns = [
    path("staffloginpage/", views.stafflogin, name='staff-login'),
    path("stafffrontpage/", views.staff_front, name='staff-front'),
    path('staffloginpage/changepassword/', views.change_password, name='change-password'),
    path('stafffrontpage/timesheet/', views.submit_timesheet, name='submit-timesheet'),
    path('timesheet/success_timesheet/', views.success_page, name='success-page'), 
    path('timesheets/<int:year>/<int:week_number>/', views.retrieve_timesheets_for_week, name='retrieve-timesheets-for-week'),
    path('create-weeks/<int:year>/', views.create_weeks_table_view, name='create-weeks'),
    path('create_weeks/success_weekcreation/', views.success_weekcreation, name='success_weekcreation'),
    path('stafffrontpage/availability', views.SubmitAvailabilityView.as_view(), name='availability'),
    path('stafffrontpage/availability/submit-availability/', views.SubmitAvailabilityView.as_view(), name='submit-availability'),
    path('stafffrontpage/availability/success-requirement/', views.SuccessAvailabilityView.as_view(), name='success_availability'),
    path('stafffrontpage/staff_weekly_timesheets/', views.StaffWeeklyTimesheetsView.as_view(), name='staff_weekly_timesheets'),
    path('stafffrontpage/download_payslip/', views.download_payslip, name='download_payslip'),
    path('stafffrontpage/scheduling_staff/', views.staff_availability_view, name='scheduling_staff'),
    path('staffloginpage/new_staff/', views.new_staff, name='new_staff'),
    path('upload/', FileUploadView.as_view(), name='file_upload'),
    path('new_staff/success_application/', views.success, name='success_application'),
    path('stafffrontpage/profile_section/', views.profile_section, name='profile_section'),

] 


