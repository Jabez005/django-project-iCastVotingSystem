from django import forms
from django.forms import ModelForm, modelformset_factory
from .models import Positions, Partylist, DynamicField

class AddPositionForm(forms.ModelForm):
    class Meta:
        model = Positions
        fields = ['Pos_name']

class AddPartyForm(forms.ModelForm):
    class Meta:
        model = Partylist
        fields = ['Party_name', 'Logo', 'Description']

class DynamicFieldForm(ModelForm):
    FIELD_TYPE_CHOICES = [
        ('text', 'Text'),
        ('email', 'Email'),
        ('number', 'Number'),
        # Add other field types here
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('time', 'Time'),
        # ... more field types as needed
    ]

    field_type = forms.ChoiceField(choices=FIELD_TYPE_CHOICES)
    class Meta:
        model = DynamicField
        fields = ['field_name', 'field_type', 'is_required', 'choices']

DynamicFieldFormset = modelformset_factory(
    DynamicField,
    form=DynamicFieldForm,
    extra=1,  # Specifies the number of empty forms to display
    can_delete=True  # Adds a boolean field to each form to mark it for deletion
)
    

def get_dynamic_form(dynamic_fields_queryset):
    class DynamicForm(forms.Form):
        # Dynamically add a choice field for positions
        position_choices = [(pos.id, pos.Pos_name) for pos in Positions.objects.all()]
        position = forms.ChoiceField(choices=position_choices, required=True)

        # Dynamically add a choice field for party lists
        partylist_choices = [(party.id, party.Party_name) for party in Partylist.objects.all()]
        partylist = forms.ChoiceField(choices=partylist_choices, required=True)

        def __init__(self, *args, **kwargs):
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
                    self.fields[field.field_name] = forms.DecimalField(**field_kwargs)
                elif field.field_type == 'integer':
                    self.fields[field.field_name] = forms.IntegerField(**field_kwargs)
                elif field.field_type == 'date':
                    self.fields[field.field_name] = forms.DateField(**field_kwargs)
                elif field.field_type == 'datetime':
                    self.fields[field.field_name] = forms.DateTimeField(**field_kwargs)
                elif field.field_type == 'time':
                    self.fields[field.field_name] = forms.TimeField(**field_kwargs)
                elif field.field_type == 'choice':
                    self.fields[field.field_name] = forms.ChoiceField(**field_kwargs)
                elif field.field_type == 'multichoice':
                    self.fields[field.field_name] = forms.MultipleChoiceField(**field_kwargs)
                elif field.field_type == 'file':
                    self.fields[field.field_name] = forms.FileField(**field_kwargs)
                elif field.field_type == 'image':
                    self.fields[field.field_name] = forms.ImageField(**field_kwargs)
                elif field.field_type == 'boolean':
                    self.fields[field.field_name] = forms.BooleanField(**field_kwargs)
                elif field.field_type == 'textarea':
                    self.fields[field.field_name] = forms.CharField(widget=forms.Textarea, **field_kwargs)
                elif field.field_type == 'url':
                    self.fields[field.field_name] = forms.URLField(**field_kwargs)
                
                
    return DynamicForm