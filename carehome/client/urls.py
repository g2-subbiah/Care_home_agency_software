from django.urls import path
from . import views

urlpatterns = [
    # agency
    path("clientloginpage/",views.clientlogin,name='client-login'),

]