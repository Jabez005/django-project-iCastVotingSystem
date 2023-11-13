from django import forms
from .models import Positions

class AddPositionForm(forms.ModelForm):
    class Meta:
        model = Positions
        fields = ['Pos_name']