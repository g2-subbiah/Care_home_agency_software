from django.urls import path
from . import views
from staff.views import create_weeks_table_view
from .views import WeeklyReportView, ClearTimeSheetsView, PayDetailProcessView, MonthlyReportView
from .views import TimesheetView, weekly_timesheets_view, monthly_timesheets_view
from django.conf import settings
from django.conf.urls.static import static

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
    path('agencyfrontpage/pay_detail/', PayDetailProcessView.as_view(), name='pay_detail'),
    path('agencyfrontpage/invoice/', MonthlyReportView.as_view(), name='invoice'),
    path('agencyfrontpage/timesheets_view/', TimesheetView.as_view(), name='timesheets_view'),
    path('timesheets_view/weekly_timesheets/', TimesheetView.as_view(), name='weekly_timesheets'),
    path('timesheets_view/monthly_timesheets/', TimesheetView.as_view(), name='monthly_timesheets'),
]


if settings.DEBUG:
    urlpatterns += static('/generated_reports/', document_root=settings.GENERATED_REPORTS_DIR)