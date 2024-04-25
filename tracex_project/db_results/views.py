"""This file contains the views for the database result app."""
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from extraction.models import PatientJourney
from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration
from db_results.forms import PatientJourneySelectForm


class MetricsOverviewView(FormView):
    """View for selecting a patient journey for showing metrics."""

    form_class = PatientJourneySelectForm
    template_name = "metrics_pj_overview.html"
    success_url = reverse_lazy("metrics_dashboard")

    def form_valid(self, form):
        """Pass selected journey to orchestrator."""
        selected_journey = form.cleaned_data["selected_patient_journey"]
        self.request.session["patient_journey_name"] = selected_journey

        return super().form_valid(form)


class MetricsDasboardView(TemplateView):
    """View for comparing the pipeline output against the ground truth."""

    template_name = "metrics_dashboard.html"
