from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField
from superadmin.models import vote_admins
from django.utils import timezone
from django.conf import settings

# Create your models here.
class CSVUpload(models.Model):
    voting_admins=models.ForeignKey('superadmin.vote_admins', on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    data = JSONField()  # Use JSONField here
    header_order = JSONField()

class Positions(models.Model):
    voting_admins=models.ForeignKey('superadmin.vote_admins', on_delete=models.CASCADE)

    Pos_name=models.CharField(max_length=100)
    Num_Candidates=models.IntegerField(default=0)
    Total_votes=models.IntegerField(default=0)
    max_candidates_elected = models.PositiveIntegerField()

    def __str__(self):
        return self.Pos_name
    
class VoterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    voting_admin = models.ForeignKey('superadmin.vote_admins', on_delete=models.CASCADE)
    org_code = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
    
class Partylist(models.Model):
    voting_admins=models.ForeignKey('superadmin.vote_admins', on_delete=models.CASCADE)
    Party_name=models.CharField(max_length=150)
    Logo=models.ImageField()
    Description=models.TextField(blank=True)
    

class DynamicField(models.Model):
    voting_admins=models.ForeignKey('superadmin.vote_admins', on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=50)  # e.g., 'text', 'email', 'number', 'date', etc.
    is_required = models.BooleanField(default=False)
    choices = JSONField(blank=True, null=True)  # For dropdowns, radios etc. Could also use a text field with a delimiter
    order = models.PositiveIntegerField(default=0)  # To keep track of the order of fields

    class Meta:
        ordering = ['order']

class CandidateApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    voting_admins=models.ForeignKey('superadmin.vote_admins', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = JSONField()  # Stores the data for each dynamic field
    positions = models.ForeignKey('Positions', on_delete=models.CASCADE)
    partylist = models.ForeignKey('Partylist', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

class Candidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming each candidate is a user
    voting_admins=models.ForeignKey('superadmin.vote_admins', on_delete=models.CASCADE)
    application = models.OneToOneField('CandidateApplication', on_delete=models.CASCADE, related_name='candidate')
    election =models.ForeignKey('Election', on_delete=models.CASCADE, related_name='candidates')
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"Candidate: {self.user.username}"

class Election(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    voting_admins = models.ManyToManyField(vote_admins, related_name='elections')
    
    def __str__(self):
        return self.name

    def start_election(self):
        self.is_active = True
        self.start_time = timezone.now()
        self.save()

    def end_election(self):
        self.is_active = False
        self.end_time = timezone.now()
        self.save()