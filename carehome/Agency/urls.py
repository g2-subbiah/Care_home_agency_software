from django.urls import path
from . import views
from staff.views import create_weeks_table_view
from .views import WeeklyReportView, ClearTimeSheetsView




urlpatterns = [
    # agency
    path("agencyloginpage/",views.agencylogin,name='agency-login'),
    path("agency/forgetpw/",views.forgetpw,name='forgetpw'),
    path("agencyfrontpage/",views.agency_front,name='agency-front'),
    path('agencyfrontpage/register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('agency-logout/', views.agency_logout, name='agency-logout'),
    path('agencyfrontpage/client_register/', views.register_client, name='client_register'),
    path('agencyfrontpage/weekly_report/', WeeklyReportView.as_view(), name='weekly_report'),
    path('clear-timesheets/', ClearTimeSheetsView.as_view(), name='clear_timesheets'),

]