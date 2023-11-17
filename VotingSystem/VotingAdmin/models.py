from django.db import models
from django.db.models import JSONField
from superadmin.models import vote_admins

# Create your models here.
class CSVUpload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    data = JSONField()  # Use JSONField here
    header_order = JSONField()

class Positions(models.Model):
    Pos_name=models.CharField(max_length=100)
    Num_Candidates=models.IntegerField(default=0)
    Total_votes=models.IntegerField(default=0)

    def __str__(self):
        return self.Pos_name