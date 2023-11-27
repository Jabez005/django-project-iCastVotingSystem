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
    election=models.ForeignKey('Election', on_delete=models.CASCADE, null=True, blank= True ,related_name='election')
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
    election = models.ForeignKey('Election', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = JSONField()  # Stores the data for each dynamic field
    positions = models.ForeignKey('Positions', on_delete=models.CASCADE, related_name='candidates')
    partylist = models.ForeignKey('Partylist', on_delete=models.CASCADE, related_name='party_list')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

class Candidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming each candidate is a user
    voting_admins=models.ForeignKey('superadmin.vote_admins', on_delete=models.CASCADE)
    application = models.OneToOneField('CandidateApplication', on_delete=models.CASCADE, related_name='candidate')
    election =models.ForeignKey('Election', on_delete=models.SET_NULL, null=True, blank=True, related_name='candidates')
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"Candidate: {self.user.username}"
    
class Election(models.Model):
    name = models.CharField(max_length=100)
    voting_admins = models.ManyToManyField(vote_admins, related_name='elections')
    is_active = models.BooleanField(default=False)

    def start_election(self):
        """Activates the election."""
        self.is_active = True
        self.save()
        self.associate_candidates()

    def end_election(self):
        """Deactivates the election."""
        self.is_active = False
        self.save()

    def associate_candidates(self):
        # Logic to associate candidates with the election
        candidate_applications = CandidateApplication.objects.filter(status='approved', election__isnull=True)
        for application in candidate_applications:
            application.election = self
            application.save()
    
    def associate_positions(self):
        # Logic to associate positions with this election
        positions = Positions.objects.filter(election__isnull=True)
        for position in positions:
            position.election = self
            position.save()

class VoterElection(models.Model):
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    has_voted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('voter', 'election')

    def __str__(self):
        return f"{self.voter} - {self.election}"

class VoteLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    vote_time = models.DateTimeField(default=timezone.now)
    position = models.ForeignKey(Positions,on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} voted in {self.election.name} at {self.vote_time}"
