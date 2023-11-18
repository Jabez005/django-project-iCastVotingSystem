from django import forms
from .models import Positions, Partylist

class AddPositionForm(forms.ModelForm):
    class Meta:
        model = Positions
        fields = ['Pos_name']

class AddPartyForm(forms.ModelForm):
    class Meta:
        model = Partylist
        fields = ['Party_name', 'Logo', 'Description']