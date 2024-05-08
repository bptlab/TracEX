"""Implementation of forms for the extraction app."""
from django import forms
from django.utils.safestring import mark_safe

from extraction.models import PatientJourney, Cohort
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
        initial=[module[0] for module in MODULES_OPTIONAL],
        help_text="If modules are deselected, the resulting dataframe will be filled with placeholders!",
    )
    event_types = forms.MultipleChoiceField(
        label="Select desired event types",
        choices=EVENT_TYPES,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        initial=EVENT_TYPES[0][0],  # [event_type[0] for event_type in EVENT_TYPES],
        help_text="'N/A' only occurs, if 'Event Type Classifier' is not selected.",
    )
    locations = forms.MultipleChoiceField(
        label="Select desired locations",
        choices=LOCATIONS,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        initial=[location[0] for location in LOCATIONS],
        help_text="'N/A' only occurs, if 'Location Extractor' is not selected.",
    )
    activity_key = forms.ChoiceField(
        label="Select activity key for output",
        choices=ACTIVITY_KEYS,
        widget=forms.RadioSelect(),
        required=True,
        initial=ACTIVITY_KEYS[0][
            0
        ],  # initialize the activity_key with event_type as key
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
            raise forms.ValidationError(
                f"{choice_1} and {choice_2} depend on each other. Please select both or none.",
                code="dependant_fields",
            )


class JourneyUploadForm(forms.ModelForm):
    """Form for uploading your own patient journey."""

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
        help_text=f"Please upload a file of type {ALLOWED_FILE_TYPES}.",
        required=True,
    )
    field_order = ["file", "name", "event_types", "locations"]


class JourneySelectForm(forms.Form):
    """Form for selecting ground truth patient journey."""

    selected_patient_journey = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={"id": "patient-journey-select"}),
    )

    def __init__(self, *args, **kwargs):
        """Initializes the PatientJourneySelectForm."""
        super().__init__(*args, **kwargs)
        self.fields[
            "selected_patient_journey"
        ].choices = self.get_patient_journey_choices()

    @staticmethod
    def get_patient_journey_choices():
        """Retrieves the available patient journey choices from the database."""
        patient_journeys = PatientJourney.manager.all()
        choices = [(pj.name, pj.name) for pj in patient_journeys]

        return choices


class FilterForm(BaseEventForm):
    """Form for selecting filter for extraction result"""

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        modules = cleaned_data.get("modules_optional") + cleaned_data.get(
            "modules_required"
        )
        activity_key = cleaned_data.get("activity_key")
        key_to_module_label = {
            "event_type": "event_type_classification",
            "activity": "activity_labeling",
            "attribute_location": "location_extraction",
        }
        if key_to_module_label[activity_key] not in modules:
            error_module = ""
            for module in MODULES_OPTIONAL:
                module_label = module[0]
                module_name = module[1]
                if module_label == key_to_module_label[activity_key]:
                    error_module = module_name
                    break
            raise forms.ValidationError(
                f"For the chosen activity key the module {error_module} has to run.\
                Select this module or change the activity key.",
            )
        self.__validate_modules_optional(modules)

        return cleaned_data

    @staticmethod
    def __validate_modules_optional(modules):
        """Validate optional modules"""
        if "metrics_analyzer" in modules and "time_extraction" not in modules:
            raise forms.ValidationError(
                "Metrics Analyzer depends on Time Extractor. Please select both or deselect Metrics Analyzer.",
                code="dependant_fields",
            )


class ResultForm(BaseEventForm):
    """Form for displaying results of event extraction."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial = kwargs.pop("initial", None)

        self.event_types = initial["event_types"]
        self.fields["event_types"].initial = self.event_types

        self.locations = initial["locations"]
        self.fields["locations"].initial = self.locations

        self.selected_modules = initial["selected_modules"]
        self.fields["modules_optional"].initial = self.selected_modules
        self.fields["modules_optional"].disabled = True


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
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    condition = forms.MultipleChoiceField(
        label="Condition:",
        choices=[],
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    preexisting_condition = forms.MultipleChoiceField(
        label="Preexisting Condition:",
        choices=[],
        widget=forms.CheckboxSelectMultiple(),
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
        """Get all choices available in the database for a given category."""
        choices = Cohort.manager.values_list(category, flat=True).distinct()
        none_info_text = mark_safe("<i>Include elements with None values</i>")
        choices = [
            (
                "None" if choice is None else choice,
                none_info_text if choice is None else choice,
            )
            for choice in choices
        ]

        # sort by name, but put None values at the beginning
        return sorted(choices, key=lambda x: (x[0] == none_info_text, x))
