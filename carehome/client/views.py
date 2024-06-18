from django.shortcuts import render

# Create your views here.
def clientlogin(request):
    return render(request,"client/clientloginpage.html")