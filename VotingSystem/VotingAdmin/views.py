import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.apps import apps
from django.contrib.auth import authenticate, login
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib import messages
from VotingSystem.settings import MEDIA_URL
from .models import  Positions, VoteLog, VoterProfile, Partylist, DynamicField, CandidateApplication, Election, Candidate
from .models import CSVUpload
from superadmin.models import vote_admins
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.forms import modelformset_factory
from .forms import AddPartyForm, DynamicFieldForm, DynamicFieldFormset, ElectionForm, VoteAdminChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from collections import OrderedDict
from django.db.models import Sum
import os
import uuid
import csv
import io
import logging
import json
from django.db.models import F
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
    voters_data_count = 0

    # Get CSVUpload objects for the logged-in admin
    csv_uploads = CSVUpload.objects.filter(voting_admins=request.user.vote_admins)

    # Iterate over each CSVUpload object and count items in the 'data' field
    for csv_upload in csv_uploads:
        # Ensure that the 'data' field is a list and count its items
        if isinstance(csv_upload.data, list):
            voters_data_count += len(csv_upload.data)

    # Fetch counts for candidate and partylists for the logged-in admin
    candidate_count = CandidateApplication.objects.filter(voting_admins=request.user.vote_admins).count()
    partylist_count = Partylist.objects.filter(voting_admins=request.user.vote_admins).count()

    context = {
        'voters': voters_data_count,
        'candidate_count': candidate_count,
        'partylist_count': partylist_count,
    }

    return render(request, 'VotingAdmin/Voting_Admin_Dash.html', context)

@login_required
def profile(request):
    vote_admin = request.user.vote_admins  # Assuming the VoteAdmin model is related to the User model
    vote_admin_form = VoteAdminChangeForm(instance=vote_admin)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        vote_admin_form = VoteAdminChangeForm(request.POST, instance=vote_admin)
        password_form = PasswordChangeForm(request.user, request.POST)

        if vote_admin_form.is_valid():
            vote_admin_form.save()
            # Redirect or add a success message

        if password_form.is_valid():
            password_form.save()
            # Redirect or add a success message

    return render(request, 'VotingAdmin/profile.html', {'vote_admin': vote_admin, 'vote_admin_form': vote_admin_form, 'password_form': password_form})

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
    last_upload = CSVUpload.objects.filter(voting_admins=request.user.vote_admins).last()
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
   
    # Filter positions by the current voting admin
    positions = Positions.objects.filter(voting_admins=request.user.vote_admins)

    context = {'Positions': positions}
    return render(request, 'VotingAdmin/Positions.html', context=context)

@login_required
def add_position_view(request):
    if request.method == 'POST':
        position_name = request.POST.get('Pos_name', '').strip()
        max_candidates = request.POST.get('max_candidates_elected')
        
        if position_name and max_candidates:
            # Convert max_candidates to an integer
            try:
                max_candidates = int(max_candidates)
            except ValueError:
                messages.error(request, 'Invalid number for max candidates elected.')
                return render(request, 'VotingAdmin/add_positions.html')

            # Get the voting admin associated with the current user
            voting_admin = get_object_or_404(vote_admins, user=request.user)
            # Create the position and associate it with the current voting admin
            position, created = Positions.objects.get_or_create(
                Pos_name=position_name,
                voting_admins=voting_admin,
                defaults={'Num_Candidates': 0, 'Total_votes': 0, 'max_candidates_elected': max_candidates}
            )
            if created:
                return JsonResponse({'status': 'ok', 'message': 'Position added successfully.'}, safe=False)
            else:
                return JsonResponse({'status': 'ok', 'message': 'Position already exists.'}, safe=False)
# Handle the error case
            return JsonResponse({'status': 'error', 'message': 'Position name and max candidates are required.'}, safe=False)
            
        else:
            messages.error(request, 'Position name and max candidates are required.')

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
    partylist = Partylist.objects.filter(voting_admins=request.user.vote_admins)  

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
            return JsonResponse({'status': 'ok', 'message': 'Party added successfully.'}, safe=False)
        else:
            return JsonResponse({'status': 'error', 'message': 'Form is not valid.'}, safe=False)

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

    if application.positions:  # Assuming there is a 'position' FK in CandidateApplication model
        Positions.objects.filter(pk=application.positions.pk).update(Num_Candidates=F('Num_Candidates') + 1)

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
    candidate = application.candidate
    candidate.status = 'rejected'
    candidate.save()


    # Retrieve email from the JSONField data
    application_data = application.data
    if isinstance(application_data, str):
        application_data = json.loads(application_data)
    email = application_data.get('Email')
        
    if email:
        send_mail(
            'Application Rejected',
            'Your application has been rejected.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        messages.success(request, "Application approved successfully.")
    else:
        messages.error(request, "No email found. Unable to send approval notification.")

    return redirect('manage_fields')  # Redirect to the desired page

@login_required
def manage_election(request):
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            election = form.save(commit=False)
            election.is_active = True  # Start the election immediately
            election.save()
            election.associate_positions() 
            election.associate_candidates()
            messages.success(request, 'Election started successfully.')
            return redirect('manage_election')  # Redirect to the manage page or dashboard
    else:
        form = ElectionForm()
        current_election = Election.objects.filter(is_active=True).first()  # Get the current active election if any
    return render(request, 'VotingAdmin/StartElection.html', {'form': form, 'current_election': current_election})

@login_required
def stop_election(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    election.end_election()
    # Redirect to the admin panel or some confirmation page
    return redirect('manage_election')

@login_required
def partylist_view(request):
    # Retrieve all partylists
    partylists = Partylist.objects.all()

    # For each partylist, we'll want to get the associated approved candidates
    for party in partylists:
        # Initialize an empty list for candidates
        party_candidate_info = []
        
        # Assuming 'approved' candidates are the ones you want to show
        candidates = CandidateApplication.objects.filter(
            partylist=party, 
            status='approved'
        )
       
        for candidate in candidates:
            candidate_data = json.loads(candidate.data) if isinstance(candidate.data, str) else candidate.data
            print(candidate_data.keys()) 
            # Append each candidate's data to the party_candidate_info list
            party_candidate_info.append({
                'full_name': f"{candidate_data.get('First Name', '')} {candidate_data.get('Last Name', '')}".strip(),
                'position': candidate.positions.Pos_name,
            })
            
        # Now we assign the filled list to the party object using setattr
        setattr(party, 'candidates', party_candidate_info)

        # Print for debugging
        print(f"Candidates for {party.Party_name}: {party.candidates}")

    # Passing the partylists with candidates to the template
    context = {
        'partylists': partylists,
    }
    return render(request, 'Voters/Partylists.html', context)

@login_required
def candidate_cards_view(request):
    temp_positions = {}
    
    for candidate in Candidate.objects.filter(application__status='approved').select_related('application__partylist', 'position'):
        data = candidate.application.data

        # Convert data to dict if it's a string (assuming it's JSON)
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                print(f"Error decoding JSON for candidate: {candidate}")
                continue  # Skip this candidate if JSON is invalid

        picture_path = data.get('Picture', None)
        picture_url = settings.MEDIA_URL + picture_path if picture_path else None  # Updated line

        first_name = data.get('First Name', '')
        last_name = data.get('Last Name', '')
        full_name = f"{first_name} {last_name}"

        position = candidate.position

        if position.id not in temp_positions:
            temp_positions[position.id] = {
                'position_name': position.Pos_name,
                'candidates': []
            }

        temp_positions[position.id]['candidates'].append({
            'full_name': full_name,
            'partylist_name': candidate.application.partylist.Party_name,
            'image_url': picture_url,
        })

    sorted_positions = OrderedDict(sorted(temp_positions.items()))
    party_lists = Partylist.objects.all()

    context = {
        'positions': sorted_positions,
        'party_lists': party_lists,
    }

    return render(request, 'Voters/Candidates copy.html', context)

@login_required
def voting_is_now_open_view(request):
    return render(request, 'Voters/VotingOpen.html')

@login_required
def voting_ended(request):
    return render(request, 'Voters/votingended.html')

@login_required
def already_voted(request):
    return render(request, 'Voters/alreadyvoted.html')

@login_required
def form_closed(request):
    return render(request,'Voters/formcloseed.html')

@login_required
def check_voting_status(request):
    try:
        current_election = Election.objects.get(is_active=True)
        
        # Check if the current user has an entry in the VoteLog for the current election
        has_voted = VoteLog.objects.filter(voter=request.user, election=current_election).exists()
        
        if has_voted:
            # Redirect to a page that says the user has already voted
            return redirect('already_voted')  # Replace 'already_voted' with the name of your url
        else:
            # Redirect to the 'Voting is now open' page
            return redirect('Voting_open')
            
    except Election.DoesNotExist:
        # If no active election exists, render the 'Voting not open' page
        return redirect('voting_ended')

@login_required
def voting_page(request):
    # Get the currently active election
    try:
        # Try to get the current active election
        current_election = Election.objects.get(is_active=True)
    except Election.DoesNotExist:
        # If no active election exists, redirect to another page, for example, 'home'
        return redirect('Not_started')
    
    positions = Positions.objects.filter(election=current_election)
    positions_with_candidates = {}

    for position in positions:
        candidate_applications = CandidateApplication.objects.filter(
            positions=position, status='approved'
        )

        candidates = []
        for application in candidate_applications:
            candidate_data = json.loads(application.data)
            first_name = candidate_data.get('First Name')
            last_name = candidate_data.get('Last Name')
            picture_path = candidate_data.get('Picture', None)
            picture_url = settings.MEDIA_URL + picture_path if picture_path else None  # Updated line
            candidate_info = {
                'id': application.id,
                'name': f"{first_name} {last_name}",
                'party': application.partylist.Party_name,
                'image_url': picture_url,
            }
            candidates.append(candidate_info)

        positions_with_candidates[position.id] = {
            'name': position.Pos_name,
            'max_candidates_elected': position.max_candidates_elected, 
            'candidates': candidates
        }

    
    context = {
    'current_election': current_election,
    'positions_with_candidates': positions_with_candidates,
}

    return render(request, 'Voters/voting_page.html', context)


@login_required
@transaction.atomic
def submit_vote(request):
    if request.method == 'POST':
        current_election = get_object_or_404(Election, is_active=True)

        if VoteLog.objects.filter(voter=request.user, election=current_election).exists():
            messages.error(request, "You have already voted in this election.")
            return redirect('Voting_success')

        positions = Positions.objects.filter(election=current_election)

        for position in positions:
            if position.max_candidates_elected > 1:
                candidate_ids = request.POST.getlist(f'position_{position.id}')
            else:
                # This handles the case where no candidate might be selected for a position
                candidate_id = request.POST.get(f'position_{position.id}')
                candidate_ids = [candidate_id] if candidate_id else []

            if candidate_ids and len(candidate_ids) > position.max_candidates_elected:
                messages.error(request, f"You can select up to {position.max_candidates_elected} candidates for {position.Pos_name}.")
                return redirect('voting_page')

            for candidate_id in candidate_ids:
                if candidate_id:  # Check if candidate_id is not None
                    try:
                        candidate = Candidate.objects.get(
                        id=candidate_id, 
                        application__positions=position,
                        application__status='approved'
                        )
                        candidate.votes = F('votes') + 1
                        candidate.save()

                        # Make sure the field name matches the model definition
                        position.Total_votes = F('Total_votes') + 1
                        position.save()

                        VoteLog.objects.create(
                        voter=request.user,
                        election=current_election,
                        position=position,
                        candidate=candidate,
                        vote_time=timezone.now()
                        )

                    except Candidate.DoesNotExist:
                    # Correct way to indicate a transaction should be rolled back in case of exception
                        raise

        messages.success(request, "Your vote has been successfully submitted.")
        return redirect('Voting_success')
    else:
        messages.error(request, "You can only submit votes using the form.")
        return redirect('voting_page')

@login_required
def latest_votes(request):
    # Get the logged-in admin's associated voting_admins instance
    # Note: Replace 'vote_admins' with your related field name if different
    vote_admin_instance = request.user.vote_admins

    # List to hold all positions with candidates and their votes for the logged-in admin
    chart_data = []

    # Get positions related to the logged-in admin
    positions = Positions.objects.filter(voting_admins=vote_admin_instance)
    print("Positions found:", positions)
    
    # For each position, prepare the data for the chart
    for position in positions:
        # List to hold candidates and their votes for the position
        candidates_data = []
        
        # Get all approved candidates for the position related to the logged-in admin
        candidates = Candidate.objects.filter(
            position=position, 
            application__status='approved',
            voting_admins=vote_admin_instance
        )
        
        # For each candidate, get their vote count
        for candidate in candidates:
            # Attempt to load the candidate information from the JSON field
            candidate_info = json.loads(candidate.application.data)
            first_name = candidate_info.get('First Name', '')
            last_name = candidate_info.get('Last Name', '')
            
            # Combine first name and last name for the full name
            full_name = f"{first_name} {last_name}".strip()

            # Append the candidate's name and votes to the candidates list
            candidates_data.append({'name': full_name, 'votes': candidate.votes})
        
        # Append the position data with its candidates to the chart_data list
        chart_data.append({'position': position.Pos_name, 'candidates': candidates_data})

    # Convert the chart data into JSON and pass it to the template
    chart_data_json = json.dumps(chart_data)
    
    print("Chart Data: ", chart_data)
    print("Number of items in Chart Data: ", len(chart_data))
    
    # Pass the JSON string to the template
    context = {'chart_data': chart_data_json}
    return render(request, 'VotingAdmin/results.html', context)

@login_required
def votes_per_position(request):
    # List to hold the total votes per position
    votes_data = []

    # Get all positions
    positions = Positions.objects.all()

    # For each position, aggregate the votes for approved candidates
    for position in positions:
        total_votes = Candidate.objects.filter(
            position=position, 
            application__status='approved'
        ).aggregate(Sum('votes'))['votes__sum'] or 0

        votes_data.append({
            'position': position.Pos_name, 
            'total_votes': total_votes
        })

    # Convert the votes data into JSON and pass it to the template
    votes_data_json = json.dumps(votes_data)

    # Pass the JSON string to the template
    context = {'votes_data': votes_data_json}
    return render(request, 'VotingAdmin/Votes_per_position.html', context)

@login_required
def print_results(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Center', parent=styles['Title'], alignment=TA_CENTER)
    
    # Fetch the most recently ended election
    most_recent_election = Election.objects.filter(
        end_date__lt=timezone.now(),
        is_active=False
    ).order_by('-end_date').first()

    # Title of the election
    election_title = most_recent_election.name if most_recent_election else 'Unknown Election'
    elements.append(Paragraph(f"Election Title: {election_title}", title_style))
    elements.append(Spacer(1, 20))  # Add space after the title

    # Centered Voting Results title
    elements.append(Paragraph("Voting Results", title_style))
    elements.append(Spacer(1, 20))  # Add space after the Voting Results title

    positions = Positions.objects.all()
    for position in positions:
        # Start with the position title in the table data
        data = [['Position: {}'.format(position.Pos_name)]]

        total_votes = 0
        candidates = Candidate.objects.filter(position=position, application__status='approved')
        for candidate in candidates:
            candidate_info = json.loads(candidate.application.data)
            first_name = candidate_info.get('First Name', 'No First Name')
            last_name = candidate_info.get('Last Name', 'No Last Name')
            data.append([f"{first_name} {last_name}: {candidate.votes} votes"])
            total_votes += candidate.votes
        data.append([f"Total Votes for {position.Pos_name}: {total_votes}"])
        # Style for the table
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ])
 
        # Create the table
        t = Table(data, colWidths=[450], hAlign='CENTER')  # Set the table width and align it to the center
        t.setStyle(table_style)
        elements.append(t)
        elements.append(Spacer(1, 20))  # Add space between tables

    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='voting_results.pdf')

@login_required
def results_page(request):
    try:
        election = Election.objects.get(is_active=True)
        messages.info(request, 'Results will be out after the election ends.')
        return redirect('results_not_open')
    except Election.DoesNotExist:
        election = Election.objects.filter(is_active=False).order_by('-id').first()

        if election:
            positions = Positions.objects.filter(election=election)
            
            results_data = []
            for position in positions:
                total_votes = position.candidates.aggregate(total=Sum('votes'))['total'] or 0

                approved_candidates = position.candidates.filter(application__status='approved')  # Adjust the filter as needed based on your model

                candidates_data = []
                for candidate in approved_candidates:
                    # Parse the JSON string into a Python dictionary
                    try:
                        candidate_data = json.loads(candidate.application.data)
                    except json.JSONDecodeError:
                        # Handle the exception if data is not properly formatted as JSON
                        candidate_data = {}

                    image_path = candidate_data.get('Picture', None)  # 'image' should be the key where the image path is stored
                    image_url = settings.MEDIA_URL + image_path if image_path else None  # Construct the full URL
                    first_name = candidate_data.get('First Name', 'N/A')
                    last_name = candidate_data.get('Last Name', 'N/A')
                    votes_percentage = (100 * candidate.votes / total_votes) if total_votes > 0 else 0

                    candidates_data.append({
                        'first_name': first_name,
                        'last_name': last_name,
                        'votes': candidate.votes,
                        'votes_percentage': votes_percentage,
                        'image_url': image_url,
                    })

                results_data.append({
                    'position_name': position.Pos_name,
                    'total_votes': total_votes,
                    'candidates': candidates_data,
                })

            context = {
                'election': election,
                'results_data': results_data,
            }
            return render(request, 'Voters/View Results 2.html', context)
        else:
            messages.error(request, 'No elections are found.')
            return redirect('Home')  