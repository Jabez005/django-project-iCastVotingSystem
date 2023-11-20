from django.db import models
from django.db.models import JSONField
from superadmin.models import vote_admins
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

    def __str__(self):
        return self.Pos_name
    
class VoterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    org_code = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
    
class Partylist(models.Model):
    voting_admins=models.ForeignKey('superadmin.vote_admins', on_delete=models.CASCADE)
    Party_name=models.CharField(max_length=150)
    Logo=models.ImageField()
    Description=models.TextField(blank=True)
    
