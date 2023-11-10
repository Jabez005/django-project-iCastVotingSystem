from django.shortcuts import render 
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from .forms import Requestform

# Create your views here.
def home(request):
    return render(request, 'votingsystembase/home.html')

def User_login(request):
     return render(request, 'votingsystembase/Users_login.html')

def Request(request):
    submitted = False
    if request.method == "POST":
        form = Requestform(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/Request?submitted=True')
    else :
        form = Requestform
        if 'submitted' in request.GET:
                submitted = True

    return render(request, 'votingsystembase/Request.html', {'form':form, 'submitted':submitted})

