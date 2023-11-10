from django.db import models

# Create your models here.
class CSVFile(models.Model):
    csv_file = models.FileField(upload_to='csv_files/')