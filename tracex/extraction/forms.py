"""Implementation of forms for the extraction app."""
import os

from django import forms

from .models import PatientJourney
from .logic.constants import EVENT_TYPES, LOCATIONS


class BaseEventForm(forms.Form):
    """Base form for event extraction forms."""

    event_types = forms.MultipleChoiceField(
        label="Select desired event types",
        choices=EVENT_TYPES,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        initial=[event_type[0] for event_type in EVENT_TYPES],
    )
    locations = forms.MultipleChoiceField(
        label="Select desired locations",
        choices=LOCATIONS,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        initial=[location[0] for location in LOCATIONS],
    )

    def clean_event_types(self):
        """Validate event types."""
        event_types = self.cleaned_data["event_types"]
        dependent_choices = [
            ("Symptom Onset", "Symptom Offset"),
            ("Hospital Admission", "Hospital Discharge"),
        ]
        for group in dependent_choices:
            self.validate_dependant_choices("event_types", group[0], group[1])

        return event_types

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        event_types = cleaned_data.get("event_types")
        locations = cleaned_data.get("locations")

        if not event_types and not locations:
            raise forms.ValidationError(
                "Please select at least one event type or one location.",
                code="no_event_type",
            )

        return cleaned_data

    def validate_dependant_choices(self, field, choice_1, choice_2):
        """Validate two choices in a form field are either both selected or none of them."""
        choices = self.cleaned_data.get(field)

        if choices is not None and ((choice_1 in choices) ^ (choice_2 in choices)):
            print("error should be raised")
            raise forms.ValidationError(
                f"{choice_1} and {choice_2} depend on each other. Please select both or none.",
                code="dependant_fields",
            )


class JourneyForm(BaseEventForm, forms.ModelForm):
    """Form for extracting events from a patient journey."""

    class Meta:
        model = PatientJourney
        fields = ["patient_journey", "name"]
        ALLOWED_FILE_TYPES = ["txt"]
        labels = {
            "patient_journey": "Patient journey",
        }
        error_messages = {
            "patient_journey": {
                "required": "Please provide a file from which to extract the event log."
            }
        }
        help_texts = {
            "name": PatientJourney.name.field.help_text,
            "patient_journey": f"Allowed file types: {', '.join(ALLOWED_FILE_TYPES)}",
        }
        widgets = {
            "patient_journey": forms.FileInput(attrs={"accept": ".txt"}),
            "name": forms.TextInput(
                attrs={"placeholder": "Name for your patient journey"}
            ),
        }

    journey_is_new = True
    field_order = ["patient_journey", "name", "event_types", "locations"]

    def clean_name(self):
        name = self.cleaned_data.get("name")
        uploaded_file = self.cleaned_data.get("patient_journey")

        if not name:
            uploaded_file_name = uploaded_file.name
            name = os.path.splitext(uploaded_file_name)[0]

        return name

    def clean_patient_journey(self):
        uploaded_file = self.cleaned_data["patient_journey"]
        patient_journey_content = uploaded_file.read().decode("utf-8")

        return patient_journey_content

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.patient_journey = self.cleaned_data["patient_journey"]
        if commit and not PatientJourney.manager.filter(name=instance.name).exists():
            instance.save()

        return instance


class GenerationForm(BaseEventForm):
    """Form for generating events from a patient journey."""


class ResultForm(BaseEventForm):
    """Form for displaying results of event extraction."""
