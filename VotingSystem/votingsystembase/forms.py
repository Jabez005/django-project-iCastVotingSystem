from django import forms
from django.forms import ModelForm
from .models import Requestform


class Requestform(forms.ModelForm):
    class Meta:
        model = Requestform
        fields = ('f_name', 'l_name', 'email', 'organization', 'details')
        labels={
            'f_name': '',
            'l_name': '',
            'email': '',
            'organization': '',
            'details': '',
        }
        widgets ={
            'f_name':forms.TextInput(attrs={'class':'form-control', 'placeholder': 'First Name'}),
            'l_name':forms.TextInput(attrs={'class':'form-control','placeholder': 'Last Name'}),
            'email':forms.EmailInput(attrs={'class':'form-control','placeholder': 'Email'}),
            'organization':forms.TextInput(attrs={'class':'form-control','placeholder': 'Organization'}),
            'details':forms.TextInput(attrs={'class':'form-control','placeholder': 'Details'}),

        }

