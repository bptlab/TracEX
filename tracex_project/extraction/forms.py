"""Implementation of forms for the extraction app."""
from django import forms

from extraction.models import PatientJourney
from tracex.logic.constants import (
    EVENT_TYPES,
    LOCATIONS,
    ACTIVITY_KEYS,
    MODULES_OPTIONAL,
    MODULES_REQUIRED,
)


class BaseEventForm(forms.Form):
    """Base form for event extraction forms."""

    modules_required = forms.MultipleChoiceField(
        label="Required modules",
        choices=MODULES_REQUIRED,
        widget=forms.CheckboxSelectMultiple(),
        required=True,
        initial=[module[0] for module in MODULES_REQUIRED],
        disabled=True,
    )
    modules_optional = forms.MultipleChoiceField(
        label="Select additional modules",
        choices=MODULES_OPTIONAL,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
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
    activity_key = forms.ChoiceField(
        label="Select activity key for output",
        choices=ACTIVITY_KEYS,
        widget=forms.RadioSelect(),
        required=True,
        initial=ACTIVITY_KEYS[0][
            0
        ],  # selects the first activity-key in the list, should be event_type
    )

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        event_types = cleaned_data.get("event_types")
        locations = cleaned_data.get("locations")
        modules = cleaned_data.get("modules_optional") + cleaned_data.get(
            "modules_required"
        )
        print(f"modules in clean: {modules}")
        activity_key = cleaned_data.get("activity_key")
        key_to_module = {
            "event_type": "event_type_classification",
            "activity": "activity_labeling",
            "attribute_location": "location_extraction",
        }
        if key_to_module[activity_key] not in modules:
            error_module = [
                module[1]
                for module in MODULES_OPTIONAL
                if module[0] == key_to_module[activity_key]
            ][0]
            raise forms.ValidationError(
                f"For the chosen activity key the module {error_module} has to run.",
            )

        if not event_types and not locations:
            raise forms.ValidationError(
                "Please select at least one event type or one location.",
                code="no_event_type",
            )

        return cleaned_data

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

    def validate_dependant_choices(self, field, choice_1, choice_2):
        """Validate two choices in a form field are either both selected or none of them."""
        choices = self.cleaned_data.get(field)

        if choices is not None and ((choice_1 in choices) ^ (choice_2 in choices)):
            print("error should be raised")
            raise forms.ValidationError(
                f"{choice_1} and {choice_2} depend on each other. Please select both or none.",
                code="dependant_fields",
            )


class JourneyForm(forms.ModelForm):
    """Form for extracting events from a patient journey."""

    class Meta:
        """Metaclass for JourneyForm, provides additional parameters for the form."""

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

    ALLOWED_FILE_TYPES = ["txt"]
    file = forms.FileField(
        label="Upload your patient journey",
        help_text=f"Please upload a file of type {ALLOWED_FILE_TYPES} containing your patient journey.",
        required=True,
    )
    field_order = ["file", "name", "event_types", "locations"]


class FilterForm(BaseEventForm):
    """Form for selecting filter for extraction result"""


class ResultForm(BaseEventForm):
    """Form for displaying results of event extraction."""

    def __init__(self, *args, selected_modules=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_modules = selected_modules
        print(f"selected_modules in result form: {selected_modules}")
        self.fields["modules_optional"].disabled = True

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        event_types = cleaned_data.get("event_types")
        locations = cleaned_data.get("locations")
        modules = self.selected_modules + cleaned_data.get("modules_required")
        print(f"modules in result clean: {modules}")
        activity_key = cleaned_data.get("activity_key")
        key_to_module = {
            "event_type": "event_type_classification",
            "activity": "activity_labeling",
            "attribute_location": "location_extraction",
        }
        if key_to_module[activity_key] not in modules:
            error_module = [
                module[1]
                for module in MODULES_OPTIONAL
                if module[0] == key_to_module[activity_key]
            ][0]
            raise forms.ValidationError(
                f"For the chosen activity key the module {error_module} has to run.",
            )

        if not event_types and not locations:
            raise forms.ValidationError(
                "Please select at least one event type or one location.",
                code="no_event_type",
            )

        return cleaned_data
