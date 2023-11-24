from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from .models import Positions, VoterProfile, Partylist, DynamicField, CandidateApplication
from .models import CSVUpload
from superadmin.models import vote_admins
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.forms import modelformset_factory
from .forms import AddPartyForm, DynamicFieldForm, DynamicFieldFormset
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import uuid
import csv
import io
import logging
import json
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

@login_required
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
    voting_admin = get_object_or_404(vote_admins, user=request.user)  # Ensure 'VotingAdmin' is the correct model

    # Retrieve all CSV uploads for this admin
    csv_uploads = CSVUpload.objects.filter(voting_admins=voting_admin)  # Ensure 'CSVUpload' model is related to 'VotingAdmin' via 'voting_admin' field

    for csv_upload in csv_uploads:
        voters_data = csv_upload.data  # Ensure 'data' is the correct field containing voters' information

        for voter in voters_data:
            email = voter['Email']
            username = email  # Assuming email is unique and used as username
            password = User.objects.make_random_password()  # Generate a secure random password

            # Ensure 'org_code' is retrieved from the 'voting_admin' instance
            org_code = voting_admin.org_code

            if not User.objects.filter(username=username).exists():
                # Create a new user
                user = User.objects.create_user(username=username, email=email, password=password)

                # Create a VoterProfile for the user
                VoterProfile.objects.create(user=user, org_code=org_code, voting_admin=voting_admin)

                # Email subject and message
                subject = "Your Voter Account Details"
                message = f"Dear Voter,\n\nYour account has been created with the following details:\n\nUsername: {username}\nPassword: {password}\nOrganization Code: {org_code}\n\nPlease change your password upon first login."

                # Send the email
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

    # Display a success message
    messages.success(request, "Voter accounts generated successfully.")

    # Redirect to a success page
    return HttpResponseRedirect(reverse('Display_data'))  # Replace 'Display_data' with your success URL name

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
def manage_fields(request):
    # Get all DynamicField objects
    fields = DynamicField.objects.all()
    applications = CandidateApplication.objects.select_related('positions', 'partylist')

    # Pass fields and applications to the context
    context = {
        'fields': fields,
        'applications': applications,
    }

    return render(request, 'VotingAdmin/Candidate_app.html', context)

@login_required
def edit_candidate_form(request):
    queryset = DynamicField.objects.filter(voting_admins=request.user.vote_admins)
    formset = DynamicFieldFormset(queryset=queryset)

    if request.method == 'POST':
        formset = DynamicFieldFormset(request.POST, queryset=queryset)
        if formset.is_valid():
            try:
                with transaction.atomic():
                    # Save with commit=False to get the form instances
                    instances = formset.save(commit=False)
                    for instance in instances:
                        # Process each instance here if needed, e.g., instance.user = request.user
                        instance.save()  # Then save the instance.

                    # Delete instances marked for deletion.
                    for instance in formset.deleted_objects:
                        instance.delete()
                    
                    # If everything is successful, redirect to the desired URL
                    return redirect('manage_fields')

            except Exception as e:
                # If an error occurs, all database changes will be rolled back.
                messages.error(request, f'An error occurred: {e}')

        else:
            # Log the formset errors
            messages.error(request, 'Please correct the errors below.')
            print(formset.errors)

    # If it's a GET request or the form is not valid, render the page with the formset
    return render(request, 'VotingAdmin/Edit_form.html', {'formset': formset})

@login_required
def field_create(request):
    # Ensure the user is a voting admin
    voting_admin = get_object_or_404(vote_admins, user=request.user)
    formset = DynamicFieldFormset(queryset=DynamicField.objects.none())  # Empty queryset as we don't want to edit existing objects here

    if request.method == 'POST':
        formset = DynamicFieldFormset(request.POST)
        if formset.is_valid():
            # Process each form in the formset
            for form in formset:
                # Check if the form has changed and it's not marked for deletion
                if form.has_changed() and not form.cleaned_data.get('DELETE', False):
                    instance = form.save(commit=False)
                    instance.voting_admins = voting_admin
                    instance.save()
            # After processing all forms, redirect to the field list
            return redirect('manage_fields')
        else:
            # If formset is not valid, you might want to add error handling here
            pass

    # If it's not a POST request, or the formset is not valid, render the page with the formset
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
            return redirect('edit_candidate_form')
    else:
        form = DynamicFieldForm(instance=field)
    return render(request, 'VotingAdmin/candidate_form.html', {'form': form})

@login_required
def field_delete(request, field_id):
    # Ensure the user is a voting admin
    voting_admin = get_object_or_404(vote_admins, user=request.user)
    field = get_object_or_404(DynamicField, id=field_id, voting_admins=voting_admin)
    field.delete()
    return redirect('edit_candidate_form')


@login_required(login_url='adminlogin')
def view_application(request, pk):
    application = get_object_or_404(CandidateApplication, id=pk)
    # Ensure the data is in dict format, as JSONField can be a string or dict
    application_data = application.data
    if isinstance(application_data, str):
        application_data = json.loads(application_data)
    context = {'application': application, 'data': application_data}
    return render(request, 'VotingAdmin/Candidate_details.html', context)

@login_required
def approve_application(request, pk):
    application = get_object_or_404(CandidateApplication, pk=pk)
    application.status = 'approved'  # Assuming 'status' is now part of CandidateApplication
    application.save()

    # Retrieve email from the JSONField data
    application_data = application.data
    if isinstance(application_data, str):
        application_data = json.loads(application_data)
    email = application_data.get('Email')  # Make sure 'email' key is correct

    if email:
        send_mail(
            'Application Approved',
            'Your application has been approved.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        messages.success(request, "Application approved successfully.")
    else:
        messages.error(request, "No email found. Unable to send approval notification.")

    return redirect('manage_fields')  # Redirect to the desired page

  

@login_required
def reject_application(request, pk):
    application = get_object_or_404(CandidateApplication, pk=pk)
    candidate = application.candidates
    candidate.status = 'rejected'
    candidate.save()


    # Retrieve email from the JSONField data
    application_data = application.data
    if isinstance(application_data, str):
        application_data = json.loads(application_data)
    email = application_data.get('Email')
        
    if email:
        send_mail(
            'Application Approved',
            'Your application has been rejected.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        messages.success(request, "Application approved successfully.")
    else:
        messages.error(request, "No email found. Unable to send approval notification.")

    return redirect('manage_fields')  # Redirect to the desired page



