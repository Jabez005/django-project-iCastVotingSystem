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


@login_required
def dynamic_form_view(request):
    if CandidateApplication.objects.filter(user=request.user).exists():
        messages.error(request, 'You have already submitted an application.')
        return redirect('form_submitted')

    dynamic_fields_queryset = DynamicField.objects.all()
    form = DynamicForm(dynamic_fields_queryset=dynamic_fields_queryset)

    if request.method == 'POST':
        form = DynamicForm(request.POST, request.FILES, dynamic_fields_queryset=dynamic_fields_queryset)
        if form.is_valid():
            with transaction.atomic():
                position = form.cleaned_data.get('position')  # This should be the ID of the position
                partylist = form.cleaned_data.get('partylist')  # This should be the ID of the partylist

                # Fetch the actual instances based on IDs provided
                position_instance = Positions.objects.get(id=position)
                partylist_instance = Partylist.objects.get(id=partylist)

                # Here you use the function to get the voting admin
                voting_admin_instance = get_voting_admin_for_user(request.user)
                if not voting_admin_instance:
                    messages.error(request, "Voting admin not found for the user.")
                    return redirect('Not_started')
                
                candidate_application = CandidateApplication(
                    user=request.user,
                    status='pending',
                    positions=position_instance,
                    partylist=partylist_instance,
                    voting_admins=voting_admin_instance
                )

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

                messages.success(request, 'Your application has been submitted successfully.')
                return redirect('Results_not_open')

    return render(request, 'Voters/Candidate_application.html', {'form': form})

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

def Results_not_open(request):
    return render(request, 'Voters/Resultsnotyetopen.html')

def form_submitted(request):
    return render(request, 'Voters/Alreadysubmitted.html')