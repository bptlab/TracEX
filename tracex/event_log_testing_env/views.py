"""This file contains the views for the event log testing environment app."""
from django.views.generic import FormView, TemplateView, View
from django.urls import reverse_lazy
from .forms import PatientJourneySelectForm
from extraction.models import PatientJourney
from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration
from .comparator import comparing_event_logs
from tracex.logic import utils


class EventLogTestingOverviewView(FormView):
    form_class = PatientJourneySelectForm
    template_name = "testing_overview.html"
    success_url = reverse_lazy("journey_filter")

    def form_valid(self, form):
        selected_journey = form.cleaned_data["selected_patient_journey"]
        patient_journey_entry = PatientJourney.manager.get(name=selected_journey)
        configuration = ExtractionConfiguration(
            patient_journey=patient_journey_entry.patient_journey,
            patient_journey_name=selected_journey,
        )
        orchestrator = Orchestrator(configuration=configuration)
        orchestrator.set_db_id_objects("patient_journey", patient_journey_entry.id)
        self.request.session["is_comparing"] = True

        return super().form_valid(form)


class EventLogTestingComparisonView(TemplateView):
    template_name = "testing_comparison.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orchestrator = Orchestrator().get_instance()
        pipeline_output_df = utils.DataFrameUtilities.get_events_df(
            patient_journey_name=orchestrator.get_configuration().patient_journey_name,
            trace_position="last",
        )
        context["xes_html"] = utils.Conversion.create_html_from_xes(
            pipeline_output_df
        ).getvalue()
        print(context["xes_html"])
        return context

    def post(self, request, *args, **kwargs):
        """Comparing a generated trace of a patient journey against the ground truth."""
        orchestrator = Orchestrator()
        patient_journey_id = orchestrator.get_db_id_objects("patient_journey")
        pipeline_output_df = orchestrator.get_data()
        comparing_event_logs(pipeline_output_df, patient_journey_id)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class EventLogTestingResultView(TemplateView):
    template_name = "testing_result.html"
