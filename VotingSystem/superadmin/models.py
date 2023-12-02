from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class vote_admins(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    emaill = models.CharField(max_length=100)
    orgz = models.CharField(max_length=100)
    org_code = models.CharField(max_length=8, unique=True)
   
class Survey(models.Model):
    question = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class Choice(models.Model):
    survey = models.ForeignKey(Survey, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)
    votes = models.IntegerField(default=0)


