from django.urls import path
from . import views

urlpatterns = [
    # client
    path("clientloginpage/",views.clientlogin,name='client-login'),
    path("clientfrontpage/", views.client_front, name='client-front'),
    path('clientloginpage/changepassword2/', views.change_password2, name='change-password2'),

]