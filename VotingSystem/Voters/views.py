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

def dynamic_form_view(request):
    
    if CandidateApplication.objects.filter(user=request.user).exists():
        # Redirect to an 'already submitted' message or page
        return redirect('already_submitted')  # Adjust the redirect as necessary

    dynamic_fields_queryset = DynamicField.objects.all()
    # Initialize the form outside of the if statement
    form = DynamicForm(dynamic_fields_queryset=dynamic_fields_queryset)  

    if request.method == 'POST':
        form = DynamicForm(request.POST, request.FILES, dynamic_fields_queryset=dynamic_fields_queryset)
        if form.is_valid():
            candidate_application = CandidateApplication()
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

            # Save the dynamic data as JSON
            candidate_application.data = json.dumps(dynamic_data)

            voting_admin = get_voting_admin_for_user(request.user)
            if voting_admin:
                candidate_application.voting_admins = voting_admin

            candidate_application.voting_admins = voting_admin

            # Save the candidate application once all fields are set
            candidate_application.save()

            # Create or get the related Candidate record
            # Create or get the related Candidate record
            candidate, created = Candidate.objects.get_or_create(
                user=request.user,  # Here the user is set to the logged-in user
                defaults={
                    'status': 'pending',
                    'votes': 0,
                    'application': candidate_application,  # Link the candidate_application
                    'voting_admins': voting_admin,
                }
            )

            # If the Candidate already existed, ensure it has the default values and link the application
            if not created:
                candidate.status = 'pending'
                candidate.votes = 0
                candidate.application = candidate_application
                candidate.voting_admin = voting_admin
                candidate.save()

            # Redirect to a success page
            return redirect('Home')  # Replace with your actual URL name
    
    # Render the form template for both GET requests and invalid form submissions
    return render(request, 'Voters/Candidate_application.html', {'form': form})


User = get_user_model()

def get_voting_admin_for_user(user):
    try:
        # Get the voter's profile which includes the org_code
        voter_profile = VoterProfile.objects.get(user=user)
        
        # Use the org_code to find the corresponding VotingAdmin from the superadmin app
        # You might need to adjust 'superadmin.VotingAdmin' if your model reference is different
        voting_admin = vote_admins.objects.get(org_code=voter_profile.org_code)
        return voting_admin
    except VoterProfile.DoesNotExist:
        # If the VoterProfile does not exist, handle this case appropriately.
        return None
    except vote_admins.DoesNotExist:
        # If a VotingAdmin with the given org_code does not exist, handle this case appropriately.
        return None