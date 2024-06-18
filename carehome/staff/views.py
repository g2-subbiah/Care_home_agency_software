from django.shortcuts import render

# Create your views here.
def stafflogin(request):
    return render(request,"staff/staffloginpage.html")