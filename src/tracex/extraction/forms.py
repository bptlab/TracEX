from django import forms
from django.core.validators import FileExtensionValidator


class BaseEventForm(forms.Form):
    # can easily be refactored and thus reduced e.g. by using constants and importing into both forms
    EVENT_TYPES = [
        ("Symptom Onset, Symptom Offset", "Symptom onset/offset"),
        ("infection", "Infection start/end"),
        ("Diagnosis", "Diagnosis"),
        ("Doctor visit", "Doctor visit"),
        ("Treatment", "Treatment"),
        ("Medication", "Medication"),
        ("Lifestyle change", "Lifestyle change"),
        ("Feelings", "Feelings"),
    ]
    LOCATIONS = [
        ("Home", "Home"),
        ("Hospital", "Hospital"),
        ("Outdoors", "Outdoors"),
    ]

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
        cleaned_data = super().clean()
        event_types = cleaned_data.get("event_types")
        locations = cleaned_data.get("locations")

        if not event_types and not locations:
            raise forms.ValidationError(
                "Please select at least one event type or one location.",
                code="no_event_type",
            )

        return cleaned_data


class JourneyForm(BaseEventForm):
    ALLOWED_FILE_TYPES = ["txt"]
    journey = forms.FileField(
        label="Patient journey",
        required=True,
        help_text=f"Allowed file types: {', '.join(ALLOWED_FILE_TYPES)}",
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_FILE_TYPES)],
        error_messages={
            "required": "Please provide a file from which to extract the event log."
        },
    )
    field_order = ["journey", "event_types", "locations"]


class GenerationForm(BaseEventForm):
    pass
