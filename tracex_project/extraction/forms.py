"""Implementation of forms for the extraction app."""
from django import forms
from django.utils.safestring import mark_safe

from extraction.models import PatientJourney, Cohort
from tracex.logic.constants import (
    EVENT_TYPES,
    LOCATIONS,
    ACTIVITY_KEYS,
)


class BaseEventForm(forms.Form):
    """Base form for event extraction forms."""

    event_types = forms.MultipleChoiceField(
        label="Select desired event types",
        choices=EVENT_TYPES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "filter-selection-field"}),
        required=False,
        initial=[event_type[0] for event_type in EVENT_TYPES],
    )
    locations = forms.MultipleChoiceField(
        label="Select desired locations",
        choices=LOCATIONS,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "filter-selection-field"}),
        required=False,
        initial=[location[0] for location in LOCATIONS],
    )
    activity_key = forms.ChoiceField(
        label="Select activity key for output",
        choices=ACTIVITY_KEYS,
        widget=forms.RadioSelect(attrs={"class": "filter-selection-field"}),
        required=True,
        initial=ACTIVITY_KEYS[0][
            0
        ],  # selects the first activity-key in the list, should be event_type
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

        # print validation errors
        print("Validation Errors: ", self.errors.as_data())

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


class EvaluationForm(BaseEventForm):
    """Form for evaluating the extraction result."""

    min_age = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"id": "min-age"}),
    )
    max_age = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"id": "max-age"}),
    )
    none_age = forms.BooleanField(
        label=mark_safe("<i>Include elements with None values</i>"),
        required=False,
        widget=forms.CheckboxInput(),
    )
    gender = forms.MultipleChoiceField(
        label="Gender:",
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={"class": "filter-selection-field"}),
        required=False,
    )
    condition = forms.MultipleChoiceField(
        label="Condition:",
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={"class": "filter-selection-field"}),
        required=False,
    )
    preexisting_condition = forms.MultipleChoiceField(
        label="Preexisting Condition:",
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={"class": "filter-selection-field"}),
        required=False,
    )
    origin = forms.MultipleChoiceField(
        label="Origin:",
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={"class": "origin-checkbox"}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Initializes the EvaluationForm."""
        config = kwargs.get("initial", None)
        super().__init__(*args, **kwargs)

        if config:
            self.fields["min_age"].initial = config.get("min_age")
            self.fields["max_age"].initial = config.get("max_age")

        self.fields["condition"].choices = self.get_choices("condition")
        self.fields["preexisting_condition"].choices = self.get_choices(
            "preexisting_condition"
        )
        self.fields["origin"].choices = self.get_choices("origin")
        self.fields["gender"].choices = self.get_choices("gender")

    @staticmethod
    def get_choices(category):
        choices = Cohort.manager.values_list(category, flat=True).distinct()
        none_info_text = mark_safe("<i>Include elements with None values</i>")
        choices = [
            (
                "None" if choice is None else choice,
                none_info_text if choice is None else choice,
            )
            for choice in choices
        ]
        return sorted(choices, key=lambda x: (x[0] == none_info_text, x))
