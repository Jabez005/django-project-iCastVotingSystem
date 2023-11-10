from django import forms
from django.forms import ModelForm
from .models import Requestform


class Requestform(forms.ModelForm):
    class Meta:
        model = Requestform
        fields = ('f_name', 'l_name', 'email', 'organization', 'details')

