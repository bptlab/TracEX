"""
Provide class-based views for the Patient Journey generator app.

Views:
JourneyGeneratorOverviewView -- View for the landing page of the Patient Journey generator.
JourneyGenerationView -- View to inspect the generated Patient Journey.
"""
import traceback

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.utils.safestring import mark_safe

from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration
from patient_journey_generator.forms import GenerationOverviewForm, GenerateProcessDescriptionForm
from patient_journey_generator.generator import generate_patient_journey, execute_generate_process_description


class JourneyGeneratorOverviewView(generic.CreateView):
    """
    View for the landing page of the Patient Journey generator.

    If a generated Patient Journey exists in the session, this view displays a form to name the Patient Journey
    and save it in the database.
    """

    form_class = GenerationOverviewForm
    template_name = "journey_generator_overview.html"
    success_url = reverse_lazy("journey_filter")

    def get_context_data(self, **kwargs):
        """Add the Patient Journey to the context to pass to the HTML file."""
        context = super().get_context_data(**kwargs)
        context["generated_journey"] = self.request.session.get("generated_journey")
        context["form"] = GenerateProcessDescriptionForm()

        return context

    def form_valid(self, form):
        """Create an empty Patient Journey instance and save the ID in the orchestrator."""
        orchestrator = Orchestrator.get_instance()
        form.instance.patient_journey = orchestrator.get_configuration().patient_journey
        response = super().form_valid(form)
        orchestrator.set_db_objects_id("patient_journey", self.object.id)

        return response


class JourneyGenerationView(generic.RedirectView):
    """
    View to inspect the generated Patient Journey.

    By passing a GET request to the view, a Patient Journey is generated and saved in the orchestrator's configuration.
    Since the JourneyGenerationView is a RedirectView, the user is redirected back to the JourneyGeneratorOverviewView.
    Therefore, this view does not render a template.
    """

    url = reverse_lazy("journey_generator_overview")

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests by generating a Patient Journey and updating the orchestrator's configuration.

        The empty Patient Journey instance from the orchestrator's configuration is modified to contain the generated
        Patient Journey text. The generated Patient Journey is also saved in the session to pass to the HTML file
        of the JourneyGenerationOverviewView.

        """
        orchestrator = Orchestrator()

        form = GenerateProcessDescriptionForm(request.GET)
        if form.is_valid():
            number_of_instances = form.cleaned_data['number_of_instances']
            degree_of_variation = form.cleaned_data['degree_of_variation']
            save_to_db = form.cleaned_data['save_to_db']
            save_as_txt = form.cleaned_data['save_as_txt']

        try:
            configuration = ExtractionConfiguration(
                patient_journey=execute_generate_process_description(
                    degree_of_variation=degree_of_variation,
                    number_of_instances=number_of_instances,
                    save_to_db=save_to_db,
                    save_as_txt=save_as_txt
                )
            )

        except Exception as e:  # pylint: disable=broad-except
            orchestrator.reset_instance()
            self.request.session.flush()

            return render(
                self.request,
                "error_page.html",
                {
                    "error_type": type(e).__name__,
                    "error_traceback": traceback.format_exc(),
                },
            )

        orchestrator.set_configuration(configuration)
        request.session[
            "generated_journey"
        ] = orchestrator.get_configuration().patient_journey

        return super().get(request, *args, **kwargs)
