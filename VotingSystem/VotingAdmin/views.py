from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import Positions, VoterProfile, Partylist, DynamicField, Candidate
from .models import CSVUpload
from superadmin.models import vote_admins
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .forms import AddPartyForm, DynamicFieldForm, DynamicFieldFormset
import uuid
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

@login_required
def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'Invalid file type.')  # You should display this message in your template
            return redirect('home')
        
        try:
            voting_admin_instance = vote_admins.objects.get(emaill=request.user.email)
        except vote_admins.DoesNotExist:
            messages.error(request, "Voting admin not found.")
            return redirect('home')  # Redirect appropriately

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
        CSVUpload.objects.create(voting_admins=voting_admin_instance, data=csv_data, header_order=header_order)

        return redirect('Display_data')  # Ensure this is the correct view name

    return render(request, 'VotingAdmin/Voters.html')

@login_required
def display_csv_data(request):
    last_upload = CSVUpload.objects.last()
    if last_upload:
        voters_data = last_upload.data
        field_names = last_upload.header_order
        upload_id = last_upload.id
    else:
        voters_data = []
        field_names = []
        upload_id = None

    # For debugging: Return the context as a JSON response
    return render(request, 'VotingAdmin/Voters.html', {
        'voters_data': voters_data,
        'field_names': field_names,
        'upload_id': upload_id,
    })

@login_required
def ManagePositions(request):
    # Get the voting admin associated with the current user
    voting_admin = get_object_or_404(vote_admins, user=request.user)
    # Filter positions by the current voting admin
    positions = Positions.objects.filter(voting_admins=voting_admin)

    context = {'Positions': positions}
    return render(request, 'VotingAdmin/Positions.html', context=context)

@login_required
def add_position_view(request):
    if request.method == 'POST':
        position_name = request.POST.get('Pos_name', '').strip()
        if position_name:
            # Get the voting admin associated with the current user
            voting_admin = get_object_or_404(vote_admins, user=request.user)
            # Create the position and associate it with the current voting admin
            position_name, created = Positions.objects.get_or_create(
                Pos_name=position_name,
                voting_admins=voting_admin,
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

@login_required
def generate_voter_accounts(request):
    # Get the voting admin associated with the current user
    voting_admin = get_object_or_404(vote_admins, user=request.user)

    # Retrieve all CSV uploads for this admin
    csv_uploads = CSVUpload.objects.filter(voting_admins=voting_admin)

    for csv_upload in csv_uploads:
        voters_data = csv_upload.data

        for voter in voters_data:
            email = voter['Email']
            username = email  # Assuming email is unique and used as username
            password = User.objects.make_random_password()  # Generate a secure password

            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, email=email, password=password)
                VoterProfile.objects.create(user=user, org_code=voting_admin.org_code)

                subject = "Your Voter Account Details"
                subject = "Your Voter Account Details"
                message = f"Dear Voter,\n\nYour account has been created. Please use the following details to log in:\n\nUsername: {username}\nPassword: {password}\n\nPlease change your password upon first login."
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

    messages.success(request, "Voter accounts generated successfully.")
    return HttpResponseRedirect(reverse('Display_data'))

@login_required
def ManageParty(request):
    # Get the voting admin associated with the current user
    voting_admin = get_object_or_404(vote_admins, user=request.user)
    partylist = voting_admin.partylist_set.all()  

    context = {'partylist': partylist}
    return render(request, 'VotingAdmin/Party.html', context=context)

@login_required
def add_party(request):
    # Get the voting admin associated with the current user
    voting_admin = get_object_or_404(vote_admins, user=request.user)

    if request.method == 'POST':
        form = AddPartyForm(request.POST, request.FILES)
        if form.is_valid():
            partylist = form.save(commit=False)
            partylist.voting_admins = voting_admin  # Set the foreign key relation
            partylist.save()
            return redirect('ManageParty')  # Redirect to the party list view
    else:
        form = AddPartyForm()

    return render(request, 'VotingAdmin/add_party.html', {'form': form})


@login_required
def field_list(request):
    # Ensure the user is a voting admin
    voting_admin = get_object_or_404(vote_admins, user=request.user)
    fields = DynamicField.objects.filter(voting_admins=voting_admin)
    return render(request, 'VotingAdmin/Candidate_app.html', {'fields': fields})

@login_required
def field_create(request):
    # Ensure the user is a voting admin
    voting_admin = get_object_or_404(vote_admins, user=request.user)
    formset = DynamicFieldFormset(queryset=DynamicField.objects.none())  # Empty queryset as we don't want to edit existing objects here

    if request.method == 'POST':
        formset = DynamicFieldFormset(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.voting_admins = voting_admin
                instance.save()
            return redirect('field_list')
    return render(request, 'VotingAdmin/candidate_form.html', {'formset': formset})

@login_required
def field_update(request, field_id):
    # Ensure the user is a voting admin
    voting_admin = get_object_or_404(vote_admins, user=request.user)
    field = get_object_or_404(DynamicField, id=field_id, voting_admins=voting_admin)
    if request.method == 'POST':
        form = DynamicFieldForm(request.POST, instance=field)
        if form.is_valid():
            form.save()
            return redirect('field_list')
    else:
        form = DynamicFieldForm(instance=field)
    return render(request, 'VotingAdmin/candidate_form.html', {'form': form})

@login_required
def field_delete(request, field_id):
    # Ensure the user is a voting admin
    voting_admin = get_object_or_404(vote_admins, user=request.user)
    field = get_object_or_404(DynamicField, id=field_id, voting_admins=voting_admin)
    field.delete()
    return redirect('field_list')



