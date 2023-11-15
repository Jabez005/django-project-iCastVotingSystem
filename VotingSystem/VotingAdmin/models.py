from django.db import models
import csv

# Create your models here.
class DynamicModel(models.Model):
    csv_file = models.FileField(upload_to='csv_files/')

    def get_fields(self):
        return [field.name for field in self._meta.fields]

    def get_values(self):
        return [getattr(self, field.name) for field in self._meta.fields]

class Positions(models.Model):
    Pos_name=models.CharField(max_length=100)
    Num_Candidates=models.IntegerField(default=0)
    Total_votes=models.IntegerField(default=0)

    def __str__(self):
        return self.Pos_name