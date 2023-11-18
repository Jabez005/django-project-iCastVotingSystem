from django import forms

class VoterLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    org_code = forms.CharField()