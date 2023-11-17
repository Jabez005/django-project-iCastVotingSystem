from django.shortcuts import render, redirect
from django.apps import apps
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.management import call_command
from .models import Positions
from .models import CSVUpload
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

#def create_dynamic_model(field_names):
    model_name = 'MyDynamicModel'
    fields = {'__module__': 'VotingAdmin.models'}  

    for field_name in field_names:
        fields[field_name] = models.CharField(max_length=255)

    model = type(model_name, (models.Model,), fields)
    return model

def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'Invalid file type.')  # You should display this message in your template
            return redirect('home')

        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        # Read the entire CSV into a list of dictionaries
        next_id = 1
        if CSVUpload.objects.exists():
            # If previous uploads exist, get the last used ID and increment by 1
            last_upload = CSVUpload.objects.last()
            last_data = last_upload.data
            if last_data:
                last_id = max(item.get('id', 0) for item in last_data)
                next_id = last_id + 1

        csv_data = []
        for row in reader:
            row['id'] = next_id
            csv_data.append(row)
            next_id += 1

        # Capture the header order from the DictReader and include the 'id'
        header_order = ['id'] + reader.fieldnames
        # Clear previous CSV data and save the new data along with header order
        CSVUpload.objects.all().delete()  # Be cautious with this!
        CSVUpload.objects.create(data=csv_data, header_order=header_order)

        # No need to save the header order in the session
        return redirect('Display_data')  # Ensure this is the correct view name

    return render(request, 'VotingAdmin/Voters.html')

def display_csv_data(request):
    last_upload = CSVUpload.objects.last()
    if last_upload:
        voters_data = last_upload.data
        field_names = last_upload.header_order
    else:
        voters_data = []
        field_names = []

    # For debugging: Return the context as a JSON response
    return render(request, 'VotingAdmin/Voters.html', {
        'voters_data': voters_data,
        'field_names': field_names,
    })

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
            
            return redirect('ManagePositions')  # Replace with your actual URL name for positions list
        else:
            messages.error(request, 'Position name is required.')

    return render(request, 'VotingAdmin/add_positions.html')
