from django.urls import path
from . import views
from .views import WeeklyReportView, ClearTimeSheetsView, MonthlyReportView, TimesheetTableView
from django.conf import settings
from django.conf.urls.static import static
from .timesheet_view import TimesheetTableView, WeeklyTimesheetsView, MonthlyTimesheetsView

urlpatterns = [
    path("agencyloginpage/",views.agencylogin,name='agency-login'),
    path("agency/forgetpw/",views.forgetpw,name='forgetpw'),
    path("agencyfrontpage/",views.agency_front,name='agency-front'),
    path('agencyfrontpage/register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('agency-logout/', views.agency_logout, name='agency-logout'),
    path('agencyfrontpage/client_register/', views.register_client, name='client_register'),
    path('agencyfrontpage/weekly_report/', WeeklyReportView.as_view(), name='weekly_report'),
    path('agencyfrontpage/clear_timesheets/', ClearTimeSheetsView.as_view(), name='clear_timesheets'),
    path('agencyfrontpage/invoice/', MonthlyReportView.as_view(), name='invoice'),
    path('agencyfrontpage/timesheets_view/', TimesheetTableView.as_view(), name='timesheets_view'),
    path('timesheets_view/weekly_timesheets/', WeeklyTimesheetsView.as_view(), name='weekly_timesheets'),
    path('timesheets_view_monthly/monthly_timesheets/', MonthlyTimesheetsView.as_view(), name='monthly_timesheets'),    
    path('agencyfrontpage/timesheets_view_monthly/', TimesheetTableView.as_view(), name='timesheets_view_monthly'),
    path('agencyfrontpage/upload_payslip/', views.upload_payslip, name='upload_payslip'),
    path('agencyfrontpage/allotments/', views.match_staff, name='allotments'),
    path('allotments/save_preferences/', views.save_preferences_logic, name='save_preferences'),
    path('agencyfrontpage/schedule_page1/', views.schedule_view, name='schedule_page1'),
    path('schedule_page1/client_schedule/', views.schedule_view, name='client_schedule'),  
    path('agencyfrontpage/schedule_page2/', views.availability_view, name='schedule_page2'),
    path('schedule_page1/staff_schedule/', views.availability_view, name='staff_schedule'),  

]


if settings.DEBUG:
    urlpatterns += static('/generated_reports/', document_root=settings.GENERATED_REPORTS_DIR)