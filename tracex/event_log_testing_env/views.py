"""This file contains the views for the event log testing environment app."""
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import PatientJourneySelectForm


class EventLogTestingOverviewView(FormView):
    form_class = PatientJourneySelectForm
    template_name = "testing_overview.html"
    success_url = reverse_lazy("testing_environment")

    def form_valid(self, form):
        # Process the form data
        selected_value = form.cleaned_data["selected_patient_journey"]
        # Perform actions based on the selected value
        return super().form_valid(form)
