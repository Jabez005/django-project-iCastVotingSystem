from django.contrib import admin

# Register your models here.
from . models import vote_admins

admin.site.register(vote_admins)