"""Implementation of forms for the extraction app."""
from typing import List, Tuple

from django import forms

from extraction.models import PatientJourney
from tracex.forms import BaseEventForm
from tracex.logic.constants import MODULES_OPTIONAL


class JourneyUploadForm(forms.ModelForm):
    """Form for uploading your own patient journey."""

    class Meta:
        """
        Configuration class for the JourneyUploadForm.

        This class specifies that the form is associated with the PatientJourney model and that it has a field for the
        'name' attribute of the PatientJourney model. It also sets the help text and widget for the 'name' field.

        Attributes:
            model: The model that this form is associated with.
            fields: The fields that this form includes.
            help_texts: Help texts for the form fields.
            widgets: Widgets to use for the form fields.
        """

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
    """Django form for selecting a patient journey from available choices in the database."""

    selected_patient_journey = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={"id": "patient-journey-select"}),
    )

    def __init__(self, *args, **kwargs):
        """Initializes the form and sets the choices for the 'selected_patient_journey' field."""
        super().__init__(*args, **kwargs)
        self.fields[
            "selected_patient_journey"
        ].choices = self.get_patient_journey_choices()

    @staticmethod
    def get_patient_journey_choices() -> List[Tuple[str, str]]:
        """Returns a list of tuples containing the names of all patient journeys from the database."""
        patient_journeys = PatientJourney.manager.all()
        choices = [
            (patient_journey.name, patient_journey.name)
            for patient_journey in patient_journeys
        ]

        return choices


class FilterForm(BaseEventForm):
    """Django form for selecting and validating extraction result filters."""

    def clean(self):
        """Validates the form data and checks module compatibility with the chosen activity key."""
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
        self.__validate_metrics_analyzer_dependency(modules)

        return cleaned_data

    @staticmethod
    def __validate_metrics_analyzer_dependency(modules):
        """Checks if 'metrics_analyzer' is selected without 'time_extraction' and raises a validation error if so."""
        if "metrics_analyzer" in modules and "time_extraction" not in modules:
            raise forms.ValidationError(
                "Metrics Analyzer depends on Time Extractor. Please select both or deselect Metrics Analyzer.",
                code="dependant_fields",
            )


class ResultForm(BaseEventForm):
    """Django form for initializing and displaying extraction results."""

    def __init__(self, *args, **kwargs):
        """Initializes the form with event types, locations, and selected modules, and disables module selection."""
        super().__init__(*args, **kwargs)
        initial = kwargs.pop("initial", None)

        self.event_types = initial["event_types"]
        self.fields["event_types"].initial = self.event_types

        self.locations = initial["locations"]
        self.fields["locations"].initial = self.locations

        self.selected_modules = initial["selected_modules"]
        self.fields["modules_optional"].initial = self.selected_modules
        self.fields["modules_optional"].disabled = True
