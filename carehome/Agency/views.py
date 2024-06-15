from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,"home.html")

def agencylogin(request):
    return render(request,"agency/agencyloginpage.html")