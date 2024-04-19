"""Implementation of forms for the trace comparator app."""
from django import forms
from extraction.models import PatientJourney


class PatientJourneySelectForm(forms.Form):
    """Form for selecting ground truth patient journey."""

    selected_patient_journey = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        """Initializes the PatientJourneySelectForm."""
        super().__init__(*args, **kwargs)
        self.fields[
            "selected_patient_journey"
        ].choices = self.get_patient_journey_choices()

    def get_patient_journey_choices(self):
        """Retrieves the available patient journey choices from the database."""
        patient_journeys = PatientJourney.manager.filter(
            name__contains="journey_comparison_"
        )
        choices = [(pj.name, pj.name) for pj in patient_journeys]

        return choices
