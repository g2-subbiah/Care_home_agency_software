from django.urls import path
from . import views

urlpatterns = [
    # client
    path("clientloginpage/",views.clientlogin,name='client-login'),
    path('clientloginpage/changepassword2/', views.change_password2, name='change-password2'),
    path('clientloginpage/clientfrontpage/', views.SubmitRequirementView.as_view(), name='client-front'),
    path('clientloginpage/clientfrontpage/submit-requirement/', views.SubmitRequirementView.as_view(), name='submit-requirement'),
    path('clientloginpage/clientfrontpage/success-requirement/', views.SuccessRequirementView.as_view(), name='success_requirement'),
]

