"""
Provide class-based views for the patient journey generator app.

Views:
JourneyGeneratorOverviewView -- View for the landing page of the patient journey generator.
JourneyGenerationView -- View to inspect the generated patient journey.
"""
import traceback

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration
from patient_journey_generator.forms import GenerationOverviewForm
from patient_journey_generator.generator import generate_patient_journey


class JourneyGeneratorOverviewView(generic.CreateView):
    """
    View for the landing page of the patient journey generator.

    If a generated patient journey exists in the session, this view displays a form to name the patient journey
    and save it in the database.
    """

    form_class = GenerationOverviewForm
    template_name = "journey_generator_overview.html"
    success_url = reverse_lazy("journey_filter")

    def get_context_data(self, **kwargs):
        """Add the patient journey to the context to pass to the HTML file."""
        context = super().get_context_data(**kwargs)
        context["generated_journey"] = self.request.session.get("generated_journey")

        return context

    def form_valid(self, form):
        """Create an empty patient journey instance and save the ID in the orchestrator."""
        orchestrator = Orchestrator.get_instance()
        form.instance.patient_journey = orchestrator.get_configuration().patient_journey
        response = super().form_valid(form)
        orchestrator.set_db_objects_id("patient_journey", self.object.id)

        return response


class JourneyGenerationView(generic.RedirectView):
    """
    View to inspect the generated patient journey.

    By passing a GET request to the view, a patient journey is generated and saved in the orchestrator's configuration.
    Since the JourneyGenerationView is a RedirectView, the user is redirected back to the JourneyGeneratorOverviewView.
    Therefore, this view does not render a template.
    """

    url = reverse_lazy("journey_generator_overview")

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests by generating a patient journey and updating the orchestrator's configuration.

        The empty patient journey instance from the orchestrator's configuration is modified to contain the generated
        patient journey text. The generated patient journey is also saved in the session to pass to the HTML file
        of the JourneyGenerationOverviewView.

        """
        orchestrator = Orchestrator()

        try:
            configuration = ExtractionConfiguration(patient_journey=generate_patient_journey())
        except Exception as e:  # pylint: disable=broad-except
            orchestrator.reset_instance()
            self.request.session.flush()

            return render(
                self.request,
                "error_page.html",
                {"error_type": type(e).__name__, "error_traceback": traceback.format_exc()}
            )

        orchestrator.set_configuration(configuration)
        request.session["generated_journey"] = orchestrator.get_configuration().patient_journey

        return super().get(request, *args, **kwargs)
