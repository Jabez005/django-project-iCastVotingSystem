from django import forms
from .models import Survey, Choice


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['question']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']