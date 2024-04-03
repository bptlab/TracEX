from django import forms
from extraction.models import PatientJourney


class PatientJourneySelectForm(forms.Form):
    selected_patient_journey = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "selected_patient_journey"
        ].choices = self.get_patient_journey_choices()

    # def get_patient_journey_choices(self):
    #     # Make a database query to retrieve the patient journey options
    #     patient_journeys = PatientJourney.objects.all()  # Retrieve all patient journeys from the database
    #     choices = [(pj.id, pj.name) for pj in patient_journeys]  # Create a list of tuples with (id, name)
    #     return choices
