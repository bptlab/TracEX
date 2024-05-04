"""Implementation of forms for the database result app."""
from django import forms
from django.db.models import Exists, OuterRef
from extraction.models import PatientJourney, Metric


class PatientJourneySelectForm(forms.Form):
    """Form for selecting a patient journey."""

    selected_patient_journey = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        """Initializes the PatientJourneySelectForm."""
        super().__init__(*args, **kwargs)
        self.fields[
            "selected_patient_journey"
        ].choices = self.get_patient_journey_choices()

    def get_patient_journey_choices(self):
        """Retrieves the available patient journey choices with exisiting metrics from the database."""
        patient_journeys = PatientJourney.manager.annotate(
            has_metrics=Exists(
                Metric.manager.filter(event__trace__patient_journey=OuterRef("pk"))
            )
        ).filter(has_metrics=True)
        choices = [(pj.name, pj.name) for pj in patient_journeys]
        return choices
