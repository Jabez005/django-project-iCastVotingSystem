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

def get_dynamic_form(dynamic_fields_queryset):
    class DynamicForm(forms.Form):
        # Dynamically add a choice field for positions
        position_choices = [(pos.id, pos.Pos_name) for pos in Positions.objects.all()]
        position = forms.ChoiceField(choices=position_choices, required=True)

        # Dynamically add a choice field for party lists
        partylist_choices = [(party.id, party.Party_name) for party in Partylist.objects.all()]
        partylist = forms.ChoiceField(choices=partylist_choices, required=True)

        for field in dynamic_fields_queryset:
            field_kwargs = {'required': field.is_required}
            if field.choices:
            # Ensure choices is a list of tuple pairs
                field_kwargs['choices'] = field.choices

        # Define form fields based on the field type
            if field.field_type == 'text':
                setattr(DynamicForm, field.field_name, forms.CharField(**field_kwargs))
            elif field.field_type == 'email':
                setattr(DynamicForm, field.field_name, forms.EmailField(**field_kwargs))
            elif field.field_type == 'number':
                setattr(DynamicForm, field.field_name, forms.DecimalField(**field_kwargs))
            elif field.field_type == 'date':
                setattr(DynamicForm, field.field_name, forms.DateField(**field_kwargs))
            elif field.field_type == 'datetime':
                setattr(DynamicForm, field.field_name, forms.DateTimeField(**field_kwargs))
            elif field.field_type == 'time':
                setattr(DynamicForm, field.field_name, forms.TimeField(**field_kwargs))
            elif field.field_type == 'choice':
                setattr(DynamicForm, field.field_name, forms.ChoiceField(**field_kwargs))
            elif field.field_type == 'multichoice':
                setattr(DynamicForm, field.field_name, forms.MultipleChoiceField(**field_kwargs))
            elif field.field_type == 'file':
                setattr(DynamicForm, field.field_name, forms.FileField(**field_kwargs))
            elif field.field_type == 'image':
                setattr(DynamicForm, field.field_name, forms.ImageField(**field_kwargs))
            elif field.field_type == 'boolean':
                setattr(DynamicForm, field.field_name, forms.BooleanField(**field_kwargs))

        # You can continue adding other field types as needed

    return DynamicForm