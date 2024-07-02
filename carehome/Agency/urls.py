from django.urls import path
from . import views
from .views import WeeklyReportView, ClearTimeSheetsView, MonthlyReportView
from .views import TimesheetTableView
from django.conf import settings
from django.conf.urls.static import static
from .timesheet_view import TimesheetTableView, WeeklyTimesheetsView, MonthlyTimesheetsView
#from staff.views import CreateWeeksTableView

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
    path('agencyfrontpage/clear_timesheets/', ClearTimeSheetsView.as_view(), name='clear_timesheets'),
    path('agencyfrontpage/invoice/', MonthlyReportView.as_view(), name='invoice'),
    path('agencyfrontpage/timesheets_view/', TimesheetTableView.as_view(), name='timesheets_view'),
    path('timesheets_view/weekly_timesheets/', WeeklyTimesheetsView.as_view(), name='weekly_timesheets'),
    path('timesheets_view/monthly_timesheets/', MonthlyTimesheetsView.as_view(), name='monthly_timesheets'),    
    #path('agencyfrontpage/create_weeks/', CreateWeeksTableView.as_view(), name='create-weeks'),

]


if settings.DEBUG:
    urlpatterns += static('/generated_reports/', document_root=settings.GENERATED_REPORTS_DIR)