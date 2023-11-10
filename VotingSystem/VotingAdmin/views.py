from django.shortcuts import render, redirect
from django.apps import apps
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db import models
from .models import CSVFile
import csv
import io
# Create your views here.

def Adminlogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff and not user.is_superuser:
            login(request, user)
            return redirect('Votingadmin')
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('Adminlogin')

    return render(request, 'authentication/Voting_adminlogin.html', {})

def Votingadmin(request):
    return render(request, 'VotingAdmin/Voting_Admin_Dash.html')

def Voters(request):
    return render(request, 'VotingAdmin/Voters.html')

def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            return HttpResponseRedirect(reverse('home'))

        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
       
        header = next(csv.reader(io_string, delimiter=','))

        # Reset the StringIO object to the beginning
        io_string.seek(0)

        # Skip the header row
        next(io_string)
        model_fields = [models.CharField(max_length=255) for _ in header]
        dynamic_model = type('DynamicCSVModel', (models.Model,), {'__module__': 'VotingAdmin.models', **{f'field{i+1}': field for i, field in enumerate(model_fields)}})
        
        apps.all_models['VotingAdmin']['dynamiccsvmodel'] = dynamic_model

        # Perform migration to create the database table for the dynamic model
        from django.core.management import call_command
        call_command('makemigrations', 'VotingAdmin')
        call_command('migrate', 'VotingAdmin')

        for column in csv.reader(io_string, delimiter=','):
            instance = dynamic_model()
            for i, value in enumerate(column):
                setattr(instance, f'field{i+1}', value)
            instance.save()
        csv_data = dynamic_model.objects.all()
    return render(request, 'VotingAdmin/Voters.html')


def display_csv_data(request):
    csv_data = CSVFile.objects.all()
    return render(request, 'VotingAdmin/Voters.html', {'csv_data': csv_data})

  