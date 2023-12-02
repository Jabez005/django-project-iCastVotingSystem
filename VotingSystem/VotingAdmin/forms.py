from django import forms
from django.forms import ModelForm, modelformset_factory
from superadmin.models import vote_admins
from .models import Positions, Partylist, DynamicField, Election
from django.core.exceptions import ValidationError
import json

class AddPositionForm(forms.ModelForm):
    class Meta:
        model = Positions
        fields = ['Pos_name', 'max_candidates_elected']

class AddPartyForm(forms.ModelForm):
    class Meta:
        model = Partylist
        fields = ['Party_name', 'Logo', 'Description']

class DynamicFieldForm(ModelForm):
    FIELD_TYPE_CHOICES = [
        ('text', 'Text'),
        ('email', 'Email'),
        ('number', 'Number'),
        ('image', 'Image'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('time', 'Time'),
        # ... more field types as needed
    ]

    field_type = forms.ChoiceField(choices=FIELD_TYPE_CHOICES)
    class Meta:
        model = DynamicField
        fields = ['field_name', 'field_type', 'is_required']

DynamicFieldFormset = modelformset_factory(
    DynamicField,
    form=DynamicFieldForm,
    extra=1,  # Specifies the number of empty forms to display
    can_delete=True  # Adds a boolean field to each form to mark it for deletion
)

class DynamicForm(forms.Form):
    def __init__(self, *args, **kwargs):
        dynamic_fields_queryset = kwargs.pop('dynamic_fields_queryset', None)
        super(DynamicForm, self).__init__(*args, **kwargs)

        for field in dynamic_fields_queryset:
            field_kwargs = {'required': field.is_required}
            if field.choices:
                field_kwargs['choices'] = [(choice, choice) for choice in field.choices]  # Assuming field.choices is a list

            # Add a field of the appropriate type to the form
            if field.field_type == 'text':
                self.fields[field.field_name] = forms.CharField(**field_kwargs)
            elif field.field_type == 'email':
                self.fields[field.field_name] = forms.EmailField(**field_kwargs)
            elif field.field_type == 'number':
                self.fields[field.field_name] = forms.IntegerField(**field_kwargs)
            elif field.field_type == 'date':
                self.fields[field.field_name] = forms.DateField(**field_kwargs)
            elif field.field_type == 'datetime':
                self.fields[field.field_name] = forms.DateTimeField(**field_kwargs)
            elif field.field_type == 'file':
                self.fields[field.field_name] = forms.FileField(**field_kwargs)
            elif field.field_type == 'image':
                self.fields[field.field_name] = forms.ImageField(**field_kwargs)
            elif field.field_type == 'textarea':
                self.fields[field.field_name] = forms.CharField(widget=forms.Textarea, **field_kwargs)
        
        # Add choice fields for positions and party lists
        position_choices = [(pos.id, pos.Pos_name) for pos in Positions.objects.all()]
        self.fields['position'] = forms.ChoiceField(choices=position_choices, required=True)
        
        partylist_choices = [(party.id, party.Party_name) for party in Partylist.objects.all()]
        self.fields['partylist'] = forms.ChoiceField(choices=partylist_choices, required=True)


    def clean_data(self):
        data = self.cleaned_data.get('data', '')
        try:
        # Try to load the JSON to ensure it's valid
            return json.loads(data)
        except json.JSONDecodeError:
            raise ValidationError('Invalid JSON format')
        
class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['name']

class VoteForm(forms.Form):
    candidate_id = forms.IntegerField(widget=forms.HiddenInput())

class VoteAdminChangeForm(forms.ModelForm):
    class Meta:
        model = vote_admins
        fields = ['first_name', 'last_name']