from django.db import models


# Create your models here.

class Requestform(models.Model):
   f_name = models.CharField(max_length=200)
   l_name = models.CharField(max_length=200)
   email = models.EmailField(max_length=100)
   organization = models.CharField(max_length=100, null=False, blank= True, default=None)
   details = models.CharField(max_length=200)
   status = models.CharField(max_length=100, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
   created = models.DateTimeField(auto_now_add=True)

   def _str_(self):
      return self.f_name + " " + self.l_name


 