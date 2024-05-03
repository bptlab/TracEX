"""Implementation of forms for the patient journey generator app."""
from django import forms
from extraction.models import PatientJourney


class GenerationOverviewForm(forms.ModelForm):
    """Form for viewing generated patient journey."""

    class Meta:
        """Metaclass for GenerationForm, provides additional parameters for the form."""

        model = PatientJourney
        fields = ["name"]
        help_texts = {
            "name": PatientJourney.name.field.help_text,
        }
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Name for your patient journey"}
            ),
        }
