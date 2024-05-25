"""Implementation of forms for the trace comparator app."""
from typing import List, Tuple

from django import forms
from extraction.models import PatientJourney


class PatientJourneySelectForm(forms.Form):
    """Form for selecting a patient journey to use in the trace testing environment."""

    selected_patient_journey = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        """Initializes the PatientJourneySelectForm with available choices."""
        super().__init__(*args, **kwargs)
        self.fields[
            "selected_patient_journey"
        ].choices = self.get_patient_journey_choices()

    @staticmethod
    def get_patient_journey_choices() -> List[Tuple[str, str]]:
        """Retrieves the available patient journey choices from the database. Available choices are those with a
        saved ground truth."""
        patient_journeys = PatientJourney.manager.filter(
            name__contains="journey_comparison_"
        )
        choices = [(pj.name, pj.name) for pj in patient_journeys]

        return choices
