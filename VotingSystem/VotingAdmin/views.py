from django.shortcuts import render, redirect
from django.apps import apps
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.management import call_command
from django.db import models
from .models import Positions
from django.apps import apps
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

    return render(request, 'authentication:Voting_adminlogin.html', {})

def Votingadmin(request):
    return render(request, 'VotingAdmin/Voting_Admin_Dash.html')

def Voters(request):
    return render(request, 'VotingAdmin/Voters.html')

def create_dynamic_model(field_names):
    model_name = 'MyDynamicModel'
    fields = {'__module__': 'VotingAdmin.models'}  

    for field_name in field_names:
        fields[field_name] = models.CharField(max_length=255)

    model = type(model_name, (models.Model,), fields)
    return model

def upload_csv(request):
    model_class = None

    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            return HttpResponseRedirect(reverse('home'))

        # Decode the uploaded file and read its contents
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string, delimiter=',')

        # Read the header row from the CSV file
        header = next(reader)

        # Define the dynamic model with the specified header row
        dynamic_model = create_dynamic_model(header)

        # Perform migration to create the database table for the dynamic model
        call_command('makemigrations')
        call_command('migrate')

        # Read the rest of the CSV file and save each row as an instance of the dynamic model
        for column in reader:
            instance = dynamic_model()
            for i, value in enumerate(column):
                setattr(instance, header[i], value)
            instance.save()

        # Store the dynamic model class name in the session for the display view to use
        request.session['dynamic_model_name'] = dynamic_model._meta.model_name

        # Redirect to the display view
        return HttpResponseRedirect(reverse('display_csv_data'))

    return render(request, 'VotingAdmin/upload_csv.html')

def display_csv_data(request):
    model_class = None
    csv_data = None
    field_names = None

    # Retrieve the dynamic model class name from the session
    dynamic_model_name = request.session.get('dynamic_model_name')

    if dynamic_model_name:
        # Fetch the dynamic model class from the app registry
        model_class = apps.get_model('your_app_label', dynamic_model_name)
        csv_data = model_class.objects.all()
        # Get the field names from the model
        if csv_data:
            field_names = [field.name for field in model_class._meta.fields if not field.auto_created]

    context = {
        'csv_data': csv_data,
        'field_names': field_names,  # Pass field names instead of model_class
    }
    return render(request, 'VotingAdmin/display_csv_data.html', context)


def ManagePositions(request):
    positions = Positions.objects.all()

    context ={'Positions' : positions}
    return render(request, 'VotingAdmin/Positions.html', context=context)
    

def add_position_view(request):
    if request.method == 'POST':
        position_name = request.POST.get('Pos_name', '').strip()
        if position_name:
            # The Num_candidates and Num_votes will be set to their default values of 0
            position_name, created = Positions.objects.get_or_create(
                Pos_name=position_name,
                defaults={'Num_Candidates': 0, 'Total_votes': 0}
            )
            if created:
                messages.success(request, 'Position added successfully.')
            else:
                messages.info(request, 'Position already exists.')
            
            return redirect('VotingAdmin/add_position')  # Replace with your actual URL name for positions list
        else:
            messages.error(request, 'Position name is required.')

    return render(request, 'VotingAdmin/add_positions.html')
