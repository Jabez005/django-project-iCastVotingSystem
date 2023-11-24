import json
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import login
from .forms import VoterLoginForm
from django.contrib.auth.decorators import login_required
from Voters.backends import VoterAuthenticationBackend
from VotingAdmin.models import DynamicField, CandidateApplication, VoterProfile, Partylist, Positions, CSVUpload, Candidate
from superadmin.models import vote_admins
from VotingAdmin.forms import DynamicForm
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

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
        # Redirect to an 'already submitted' message or page
        return redirect('Home')  # Adjust the redirect as necessary

    dynamic_fields_queryset = DynamicField.objects.all()
    form = DynamicForm(dynamic_fields_queryset=dynamic_fields_queryset)  

    if request.method == 'POST':
        form = DynamicForm(request.POST, request.FILES, dynamic_fields_queryset=dynamic_fields_queryset)
        if form.is_valid():
            candidate_application = CandidateApplication(user=request.user)  # Set the user here
            dynamic_data = {}
            # Populate dynamic fields and collect data for JSON
            for field in dynamic_fields_queryset:
                field_name = field.field_name
                field_value = form.cleaned_data.get(field_name)

                if isinstance(field_value, InMemoryUploadedFile):
                    # Save the file and store the path in the dynamic_data
                    file_path = default_storage.save(field_value.name, ContentFile(field_value.read()))
                    field_value = file_path

                dynamic_data[field_name] = field_value
            
            # Handle 'positions' and 'partylist' fields
            candidate_application.positions_id = form.cleaned_data.get('position')
            candidate_application.partylist_id = form.cleaned_data.get('partylist')
            candidate_application.data = json.dumps(dynamic_data)

            voting_admin = get_voting_admin_for_user(request.user)
            if voting_admin:
                candidate_application.voting_admins = voting_admin

            candidate_application.save()  # Save after all fields are set

            candidate, created = Candidate.objects.get_or_create(
                user=request.user,  # Here the user is set to the logged-in user
                defaults={
                    'status': 'pending',
                    'votes': 0,
                    'application': candidate_application,  # Link the candidate_application
                    'voting_admins': voting_admin,
                }
            )

            if not created:
                candidate.status = 'pending'
                candidate.votes = 0
                candidate.application = candidate_application
                candidate.voting_admin = voting_admin
                candidate.save()

            return redirect('Home')  # Replace with your actual URL name

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