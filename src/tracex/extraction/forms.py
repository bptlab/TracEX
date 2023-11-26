from django import forms
from django.core.validators import FileExtensionValidator


class JourneyForm(forms.Form):
    ALLOWED_FILE_TYPES = ["txt"]
    EVENT_TYPES = [
        ("symptoms", "Symptom onset/offset"),
        ("infection", "Infection start/end"),
        ("diagnosis", "Diagnosis"),
        ("doctor_visit", "Doctor visit"),
        ("treatment", "Treatment"),
        ("medication", "Medication"),
        ("lifestyle change", "Lifestyle change"),
        ("feelings", "Feelings"),
    ]
    LOCATIONS = [
        ("home", "Home"),
        ("hospital", "Hospital"),
        ("outdoors", "Outdoors"),
    ]

    journey = forms.FileField(
        label="Patient journey",
        required=True,
        help_text=f"Allowed file types: {', '.join(ALLOWED_FILE_TYPES)}",
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_FILE_TYPES)],
        error_messages={
            "required": "Please provide a file from which to extract the event log."
        },
    )
    event_types = forms.MultipleChoiceField(
        label="Select desired event types",
        choices=EVENT_TYPES,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    locations = forms.MultipleChoiceField(
        label="Select desired locations",
        choices=LOCATIONS,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        event_types = cleaned_data.get("event_types")
        locations = cleaned_data.get("locations")

        if not event_types and not locations:
            raise forms.ValidationError(
                "Please select at least one event type or one location.",
                code="no_event_type",
            )

        return cleaned_data


class GenerationForm(forms.Form):
    # can easily be refactored and thus reduced e.g. by using constants and importing into both forms
    ALLOWED_FILE_TYPES = ["txt"]
    EVENT_TYPES = [
        ("symptoms", "Symptom onset/offset"),
        ("infection", "Infection start/end"),
        ("diagnosis", "Diagnosis"),
        ("doctor_visit", "Doctor visit"),
        ("treatment", "Treatment"),
        ("medication", "Medication"),
        ("lifestyle change", "Lifestyle change"),
        ("feelings", "Feelings"),
    ]
    LOCATIONS = [
        ("home", "Home"),
        ("hospital", "Hospital"),
        ("outdoors", "Outdoors"),
    ]

    event_types = forms.MultipleChoiceField(
        label="Select desired event types",
        choices=EVENT_TYPES,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    locations = forms.MultipleChoiceField(
        label="Select desired locations",
        choices=LOCATIONS,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        event_types = cleaned_data.get("event_types")
        locations = cleaned_data.get("locations")

        if not event_types and not locations:
            raise forms.ValidationError(
                "Please select at least one event type or one location.",
                code="no_event_type",
            )

        return cleaned_data
