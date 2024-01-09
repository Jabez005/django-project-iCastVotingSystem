import json
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import login
from .forms import VoterLoginForm
from django.contrib.auth.decorators import login_required
from Voters.backends import VoterAuthenticationBackend
from VotingAdmin.models import DynamicField, CandidateApplication, VoterProfile, Partylist, Positions, CSVUpload, Candidate, Election
from superadmin.models import vote_admins
from VotingAdmin.forms import DynamicForm
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.db.models import F 

# Create your views here.


def voter_login(request):
    error_message = None
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
                error_message = 'Invalid login credentials.'
    else:
        form = VoterLoginForm()
    return render(request, 'authentication/voter_login.html', {'form': form, 'error_message': error_message})

def home(request):
    return render(request, 'Voters/Home.html')

@login_required
def dynamic_form_view(request):
    election_ongoing = Election.objects.filter(is_active=True).exists()
    form_submitted = False  # Add this variable to track form submission
    error_message = None

    if CandidateApplication.objects.filter(user=request.user).exists():
        error_message = 'You have already submitted an application.'
        return render(request, 'Voters/Candidate_application.html', {'error_message': error_message})

    dynamic_fields_queryset = DynamicField.objects.all()
    form = DynamicForm(dynamic_fields_queryset=dynamic_fields_queryset)

    if request.method == 'POST':
        form_submitted = True  # Update the variable when the form is submitted
        if election_ongoing:
            # Only add the message if the form was actually submitted
            error_message = 'Election is currently ongoing. Candidate application submissions are closed.'
            # Render the form with the message
            return render(request, 'Voters/Candidate_application.html', {
                'form': form,
                'election_ongoing': election_ongoing,
                'error_message': error_message,
                'form_submitted': form_submitted,  # Pass the new variable to the template
            })
        else:
            form = DynamicForm(request.POST, request.FILES, dynamic_fields_queryset=dynamic_fields_queryset)
            if form.is_valid():
                with transaction.atomic():
                    # Extract cleaned data from the form
                    position = form.cleaned_data.get('position')
                    partylist = form.cleaned_data.get('partylist')

                    # Fetch actual instances based on provided IDs
                    position_instance = Positions.objects.get(id=position)
                    partylist_instance = Partylist.objects.get(id=partylist)

                    # Create a new CandidateApplication
                    candidate_application = CandidateApplication(
                        user=request.user,
                        status='pending',
                        positions=position_instance,
                        partylist=partylist_instance,
                        # Assuming you have a function `get_voting_admin_for_user`
                        voting_admins=get_voting_admin_for_user(request.user)  
                    )

                    # Store the dynamic data as JSON
                    dynamic_data = {}
                    for field in dynamic_fields_queryset:
                        field_name = field.field_name
                        field_value = form.cleaned_data.get(field_name)
                        if isinstance(field_value, InMemoryUploadedFile):
                            file_path = default_storage.save(field_value.name, ContentFile(field_value.read()))
                            field_value = file_path
                        dynamic_data[field_name] = field_value
                    candidate_application.data = json.dumps(dynamic_data)
                    candidate_application.save()

                    # Create or update the Candidate model
                    candidate, created = Candidate.objects.get_or_create(
                        user=request.user,
                        defaults={
                            'votes': 0,
                            'application': candidate_application,
                            'position': position_instance,
                            'voting_admins': candidate_application.voting_admins,
                        }
                    )
                    if not created:
                        candidate.application = candidate_application
                        candidate.save()

                    # Redirect to the home page after a successful submission
                    messages.success(request, 'Your application has been submitted successfully.')
                    return redirect('Home')

    # Render the form template
    return render(request, 'Voters/Candidate_application.html', {
        'form': form,
        'election_ongoing': election_ongoing,
        'form_submitted': form_submitted,
        'error_message': error_message,
    })

User = get_user_model()

def get_voting_admin_for_user(user):
    try:
        voter_profile = VoterProfile.objects.get(user=user)
        return voter_profile.voting_admin
    except VoterProfile.DoesNotExist:
        # If the VoterProfile does not exist, handle this case appropriately.
        return None
    except vote_admins.DoesNotExist:
        # If a VotingAdmin with the given org_code does not exist, handle this case appropriately.
        return None

@login_required
def show_candidates(request):
    partylist_data = []

    partylists = Partylist.objects.all()
    for party in partylists:
        party_data = {
            'partylist_name': party.Party_name,
            'candidates': []
        }

        # Get all candidates for the partylist
        candidates = Candidate.objects.filter(partylist=party).select_related('position')

        for candidate in candidates:
            candidate_data = {
                'name': f"{candidate.first_name} {candidate.last_name}",
                'position': candidate.position.name
            }
            party_data['candidates'].append(candidate_data)

        if party_data['candidates']:
            partylist_data.append(party_data)

    return render(request, 'Voter/Candidates.html', {'partylists': partylist_data})

def Not_started(request):
    return render(request, 'Voters/Election_not_started.html')

def Ended(request):
    return render(request, 'Voters/election_ended.html')

def Voting_success(request):
    return render(request, 'Voters/votesuccess.html')

def form_submitted(request):
    return render(request, 'Voters/Alreadysubmitted.html')

def results_not_open(request):
    return render(request, 'Voters/Resultsnotyetopen.html')