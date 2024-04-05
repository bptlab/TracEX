"""This file contains the views for the patient journey generator app."""
from django.urls import reverse_lazy
from django.views import generic

from extraction.forms import GenerationForm
from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration
from patient_journey_generator.generator import generate_patient_journey
from tracex.logic import constants

IS_TEST = False  # Controls the presentation mode of the pipeline, set to False if you want to run the pipeline


class JourneyGeneratorOverviewView(generic.TemplateView):
    """View for the landing page of the patient journey generator."""

    template_name = "journey_generator_overview.html"


class JourneyGenerationView(generic.CreateView):
    """View for generating a patient journey."""

    form_class = GenerationForm
    template_name = "journey_generation.html"
    success_url = reverse_lazy("processing")

    def get_context_data(self, **kwargs):
        """Generate a patient journey and save it in the cache."""
        context = super().get_context_data(**kwargs)
        orchestrator = Orchestrator()

        if IS_TEST:
            with open(
                str(constants.input_path / "journey_synth_covid_1.txt"), "r"
            ) as file:
                journey = file.read()
                configuration = ExtractionConfiguration(patient_journey=journey)
                orchestrator.set_configuration(configuration)
        else:
            configuration = ExtractionConfiguration(
                patient_journey=generate_patient_journey()
            )
            orchestrator.set_configuration(configuration)

        context["generated_journey"] = orchestrator.configuration.patient_journey
        return context

    def form_valid(self, form):
        """Save the generated journey in the orchestrator's configuration."""
        self.request.session["is_extracted"] = False
        orchestrator = Orchestrator.get_instance()
        orchestrator.configuration.update(
            # This should not be necessary, unspecefied values should be unchanged
            patient_journey=orchestrator.configuration.patient_journey,
            event_types=form.cleaned_data["event_types"],
            locations=form.cleaned_data["locations"],
        )
        form.instance.patient_journey = orchestrator.configuration.patient_journey
        response = super().form_valid(form)
        orchestrator.db_objects["patient_journey"] = self.object.id

        return response
