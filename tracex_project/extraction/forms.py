"""Implementation of forms for the extraction app."""
from django import forms

from extraction.models import PatientJourney, Cohort
from tracex.forms import BaseEventForm
from tracex.logic.constants import MODULES_OPTIONAL


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
