"""Implementation of forms for the extraction app."""
import os

from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

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
        # TODO: Move this to clean_event_types
        dependent_choices_groups = [
            ("Symptom Onset", "Symptom Offset"),
            ("Hospital Admission", "Hospital Discharge"),
        ]
        for group in dependent_choices_groups:
            self.validate_dependant_choices("event_types", group[0], group[1])

        return cleaned_data

    def validate_dependent_fields(self, field):
        """Validate that two fields is selected together or not at all."""
        dependent_choices_groups = [
            ("Symptom Onset", "Symptom Offset"),
            ("Hospital Admission", "Hospital Discharge"),
        ]
        selected_fields = self.cleaned_data[field]
        for group in dependent_choices_groups:
            if all(selected_fields) or not any(selected_fields):
                continue

            raise forms.ValidationError(
                f"The fields {', '.join(group)} depend on each other. Please select all or none.",
                code="dependent_fields",
            )

    def validate_dependant_choices(self, field, choice_1, choice_2):
        """Validate two choices in a form field are either both selected or none of them."""
        choices = self.cleaned_data.get(field)

        if (choice_1 in choices) ^ (choice_2 in choices):
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
    journey_is_new = True
    patient_journey = forms.FileField(
        label="Patient journey",
        required=True,
        help_text=f"Allowed file types: {', '.join(ALLOWED_FILE_TYPES)}",
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_FILE_TYPES)],
        error_messages={
            "required": "Please provide a file from which to extract the event log."
        },
    )
    name = forms.CharField(
        label="Name for your patient journey",
        required=False,
        help_text=PatientJourney.name.field.help_text,
    )
    field_order = ["patient_journey", "name", "event_types", "locations"]

    def clean_name(self):
        name = self.cleaned_data.get("name")
        uploaded_file = self.cleaned_data.get("patient_journey")

        if not name:
            uploaded_file_name = uploaded_file.name
            name = os.path.splitext(uploaded_file_name)[0]

        return name

    def clean_patient_journey(self):
        print("clean_patient_journey")
        patient_journey = self.cleaned_data["patient_journey"]
        try:
            instance = PatientJourney.objects.get(patient_journey=patient_journey)
            self.journey_is_new = False

            return (
                instance.patient_journey
            )  # Return existing instance from the database
        except PatientJourney.DoesNotExist:
            print("is New")
            return patient_journey  # Continue with default validation


class GenerationForm(BaseEventForm):
    """Form for generating events from a patient journey."""


class ResultForm(BaseEventForm):
    """Form for displaying results of event extraction."""
