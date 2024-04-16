"""This file contains the views for the patient journey generator app."""
from django.urls import reverse_lazy
from django.views import generic

from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration
from patient_journey_generator.forms import GenerationOverviewForm
from patient_journey_generator.generator import generate_patient_journey
from tracex.logic import constants


IS_TEST = False  # Controls the presentation mode of the pipeline, set to False if you want to run the pipeline


class JourneyGeneratorOverviewView(generic.CreateView):
    """View for the landing page of the patient journey generator."""

    form_class = GenerationOverviewForm
    template_name = "journey_generator_overview.html"
    success_url = reverse_lazy("journey_filter")

    def get_context_data(self, **kwargs):
        """Add the patient journey to the context."""
        context = super().get_context_data(**kwargs)
        context["generated_journey"] = self.request.session.get("generated_journey")

        return context

    def form_valid(self, form):
        """Save the generated journey in the orchestrator's configuration."""
        orchestrator = Orchestrator.get_instance()
        form.instance.patient_journey = orchestrator.configuration.patient_journey
        response = super().form_valid(form)
        orchestrator.db_objects["patient_journey"] = self.object.id

        return response


class JourneyGenerationView(generic.RedirectView):
    """View for the patient journey generation"""

    url = reverse_lazy("journey_generator_overview")

    def get(self, request, *args, **kwargs):
        """Generate a patient journey and save it in the cache."""
        orchestrator = Orchestrator()
        if IS_TEST:
            with open(
                str(constants.input_path / "journey_synth_covid_1.txt"), "r"
            ) as file:
                journey = file.read()
            configuration = ExtractionConfiguration(patient_journey=journey)
            orchestrator.set_configuration(configuration)
            self.request.session["generated_journey"] = journey
        else:
            # This automatically updates the configuration with the generated patient journey
            configuration = ExtractionConfiguration(
                patient_journey=generate_patient_journey()
            )
            orchestrator.set_configuration(configuration)
            request.session[
                "generated_journey"
            ] = orchestrator.configuration.patient_journey
        return super().get(request, *args, **kwargs)
