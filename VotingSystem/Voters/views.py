from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import VoterLoginForm
from Voters.backends import VoterAuthenticationBackend

# Create your views here.

def voter_login(request):
    if request.method == 'POST':
        form = VoterLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            org_code = form.cleaned_data['org_code']

            user = VoterAuthenticationBackend().authenticate(request, username=username, password=password, org_code=org_code)
            if user is not None:
                login(request, user, backend='Voters.backends.VoterAuthenticationBackend')
                return redirect('Home')  # Redirect to voter's dashboard view
            else:
                form.add_error(None, "Invalid credentials.")
    else:
        form = VoterLoginForm()
    return render(request, 'authentication/voter_login.html', {'form': form})

def home(request):
    return render(request, 'Voters/Home.html')
