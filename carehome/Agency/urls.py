from django.urls import path
from . import views

urlpatterns = [
    # agency
    path("agencyloginpage/",views.agencylogin,name='login-page')
    path("forgetpw/",views.forgetpw,name='forgetpw')








    # staff






    # client




]