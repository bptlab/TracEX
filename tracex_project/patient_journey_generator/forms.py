"""Implementation of forms for the Patient Journey generator app."""
from django import forms
from extraction.models import PatientJourney


class GenerationOverviewForm(forms.ModelForm):
    """
    Form for generating a Patient Journey.

    By submitting this form, a Patient Journey is generated and saved in the orchestrator's configuration.
    """

    class Meta:
        """
        Metaclass that provides additional information.

        Attributes:
        model -- The model to use for the form.
        fields -- The fields to include in the form.
        help_texts -- The help texts for the fields.
        widgets -- The widgets for the fields.
        - "name" - A text input field to name the Patient Journey. Required, to save Patient Journey in the database.
        """

        model = PatientJourney
        fields = ["name"]
        help_texts = {
            "name": PatientJourney.name.field.help_text,
        }
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Name for your Patient Journey"}
            ),
        }
