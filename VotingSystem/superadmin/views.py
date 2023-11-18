from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
import random
import uuid
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings

from votingsystembase.models import Requestform
from superadmin.models import vote_admins

# Create your views here.

def login_superuser(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('Superadmin')
        else:
            messages.success(request, ("Username and Password do not match. Please try again"))
            return redirect('login_superuser')
    else:
        return render(request, 'authentication/adminlogin.html', {})
    
def Superadmin(request):
    return render(request, 'superadmin/Superadmin.html')


@login_required(login_url='requests')
def requests(request):

    my_records = Requestform.objects.all()

    context ={'Requestform' : my_records}
    return render(request, 'superadmin/requests.html', context = context)


@login_required(login_url='requests')
def singular_request(request, pk):

    all_records = Requestform.objects.get(id=pk)

    context ={'Requestform' : all_records}
    return render(request, 'superadmin/view_request.html', context = context)


def generate_organization_code():
    """Generates a random 8-character organization code."""

    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    organization_code = ""
    for i in range(8):
        organization_code += random.choice(characters)

    return organization_code


def approve_request(request, request_id):
    # Start a transaction
    with transaction.atomic():
        # Get the request or return a 404 error if it doesn't exist
        request_form = get_object_or_404(Requestform, id=request_id)

        # Check if the request is already approved to avoid duplicating vote_admins entries
        if request_form.status== 'approved':
            messages.error(request, "This request has already been approved.")
            return redirect('requests')

        # Approve the request
        request_form.status = True
        request_form.status = "approved"
        request_form.save()

        # Generate an organization code
        organization_code = generate_organization_code()

        # Create a new vote_admins instance
        admins = vote_admins()
        admins.first_name =  request_form.f_name
        admins.last_name = request_form.l_name
        admins.emaill = request_form.email
        admins.orgz = request_form.organization
        admins.org_code = organization_code
        admins.save()

    # Redirect to the list of requests
    return redirect('requests')

def reject_request(request, request_id):
    request = Requestform.objects.get(id=request_id)
    request.approved = False
    request.status = "Rejected"
    request.save()

    return redirect('requests')

@login_required(login_url='admins')
def voting_admins(request):

    admin_records = vote_admins.objects.all()

    context ={'vote_admins' : admin_records}
    return render(request, 'superadmin/admins.html', context = context)


def generate_admin_account(request, admin_id):
    try:
        admin_record = vote_admins.objects.get(id=admin_id)
    except vote_admins.DoesNotExist:
        return "Voting admin not found."

    username = admin_record.emaill
    email = admin_record.emaill
    generated_uuid = uuid.uuid4()
    password = generated_uuid.hex[0:6]

    user = User.objects.create_user(username=email, password=password, email=email)
    user.is_staff = True
    user.save()

    # Link the User instance to the vote_admins instance
    admin_record.user = user
    admin_record.save()

    # Send an email to the voting admin with the password
    subject = "Your Voting Admin Account"
    message = f"Dear {admin_record.first_name},\n\nYour voting admin account has been created with the following details:\n\nUsername: {admin_record.emaill}\nPassword: {password}\n\nPlease log in to the system using these credentials. You can change your password after logging in.\n\nThank you."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [admin_record.emaill]

    send_mail(subject, message, from_email, recipient_list)

    return render(request, 'sending_email.html', {'email': email, 'password': password})

    