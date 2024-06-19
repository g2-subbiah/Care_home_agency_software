from django.urls import path
from . import views

urlpatterns = [
    # agency
    path("agencyloginpage/",views.agencylogin,name='agency-login'),
    path("agency/forgetpw/",views.forgetpw,name='forgetpw'),
    path("agencyfrontpage/",views.agency_front,name='agency-front'),
    path('agencyfrontpage/register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('agency-logout/', views.agency_logout, name='agency-logout'),
    path('agencyfrontpage/client_register/', views.register_client, name='client_register'),


]