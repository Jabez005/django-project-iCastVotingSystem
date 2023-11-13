from django.shortcuts import render, redirect
from django.apps import apps
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.management import call_command
from django.db import models
from .models import Positions
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

def create_dynamic_model(file_path):
    model_name = 'MyDynamicModel'
    fields = {}

    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)

        for field_name in header:
            fields[field_name] = models.CharField(max_length=255)

    model = type(model_name, (models.Model,), fields)
    return model


def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            return HttpResponseRedirect(reverse('home'))

        # Decode the uploaded file and read its contents
        decoded_file = csv_file.read().decode('utf-8')

        # Create a CSV reader object from the decoded file contents
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string, delimiter=',')

        # Read the header row from the CSV file
        header = next(reader)

        # Define the dynamic model with the specified header row
        dynamic_model = create_dynamic_model(header)

        # Perform migration to create the database table for the dynamic model
        call_command('makemigrations', 'VotingAdmin')
        call_command('migrate', 'VotingAdmin')

        # Read the rest of the CSV file and save each row as an instance of the dynamic model
        for column in reader:
            instance = dynamic_model()
            for i, value in enumerate(column):
                setattr(instance, header[i], value)
            instance.save()

        csv_data = dynamic_model.objects.all()
    return render(request, 'VotingAdmin/Voters.html', {'csv_data': csv_data})

def display_csv_data(request, model):
    csv_data = model.objects.all()
    return render(request, 'VotingAdmin/Voters.html', {'csv_data': csv_data})

def ManagePositions(request):
    return render(request, 'VotingAdmin/Positions.html')

def add_position_view(request, ):
    if request.method == 'POST':
        position_name = request.POST['Pos_name']

        add_position_view(request, position_name)

        messages.success(request, 'Position added successfully.')

        return redirect('voting_admin:positions')

    return render(request, 'VotingAdmin/add_positions.html')
