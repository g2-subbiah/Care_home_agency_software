from django.urls import path
from . import views

urlpatterns = [
    # agency
    path("staffloginpage/",views.stafflogin,name='staff-login'),

]