"""
This file contains the views for the extraction app.
Some unused imports and variables have to be made because of architectural requirement.
"""

import traceback

# pylint: disable=unused-argument, unused-variable

import pandas as pd
from typing import Dict, List

from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
from django.shortcuts import redirect, render

from extraction.forms import (
    JourneyUploadForm,
    ResultForm,
    FilterForm,
    JourneySelectForm,
)
from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration
from extraction.models import PatientJourney
from tracex.views import DownloadXesView
from tracex.logic import utils


class JourneyInputSelectView(generic.TemplateView):
    """A Django view that renders a template for the user to choose the patient journey input method."""

    template_name = "choose_input_method.html"


class JourneyUploadView(generic.CreateView):
    """A Django view that handles the uploading of a patient journey."""

    form_class = JourneyUploadForm
    template_name = "upload_journey.html"

    def form_valid(self, form):
        """Overrides the form_valid method to save the uploaded journey in the cache."""
        uploaded_file = self.request.FILES.get("file")
        content = uploaded_file.read().decode("utf-8")
        form.instance.patient_journey = content
        response = super().form_valid(form)

        return response

    def get_success_url(self):
        """Overrides the get_success_url method to provide the URL to redirect to after a successful file upload."""

        return reverse_lazy("journey_details", kwargs={"pk": self.object.id})


class JourneySelectView(generic.FormView):
    """A Django view that handles the selection of a patient journey from the database."""

    model = PatientJourney
    form_class = JourneySelectForm
    template_name = "select_journey.html"
    success_url = reverse_lazy("journey_details")

    def form_valid(self, form):
        """Overrides the form_valid method to redirect to the journey details view after a valid form submission."""
        selected_journey = form.cleaned_data["selected_patient_journey"]
        patient_journey_entry = PatientJourney.manager.get(name=selected_journey)

        return redirect("journey_details", pk=patient_journey_entry.pk)


class JourneyDetailView(generic.DetailView):
    """A Django view that displays the details of a selected patient journey."""

    model = PatientJourney
    template_name = "journey_details.html"

    def get_context_data(self, **kwargs):
        """Overrides the get_context_data method to add the patient journey to the context data."""
        context = super().get_context_data(**kwargs)
        patient_journey = self.get_object()
        context["patient_journey"] = patient_journey
        self.request.session["patient_journey_id"] = patient_journey.id

        return context

    def post(self, request, *args, **kwargs):
        """Overrides the post method to redirect to the filter view after a POST request."""
        patient_journey_id = self.request.session.get("patient_journey_id")
        patient_journey = PatientJourney.manager.get(pk=patient_journey_id)
        configuration = ExtractionConfiguration(
            patient_journey=patient_journey.patient_journey
        )
        orchestrator = Orchestrator(configuration)
        orchestrator.set_db_objects_id("patient_journey", patient_journey_id)

        return redirect("journey_filter")


class JourneyFilterView(generic.FormView):
    """A Django view that handles the selection of extraction results filter."""

    form_class = FilterForm
    template_name = "filter_journey.html"
    success_url = reverse_lazy("result")

    def get_context_data(self, **kwargs):
        """Overrides the get_context_data method to add the 'is_comparing' session variable to the context data."""
        context = super().get_context_data(**kwargs)
        context["is_comparing"] = self.request.session.get("is_comparing")

        return context

    def form_valid(self, form):
        """
        Run the extraction pipeline and save the filter settings in the Orchestrator's configuration.

        This method is called when the form is valid. It updates the Orchestrator's configuration
        with the form data, reduces the modules to the selected ones, and runs the extraction pipeline.
        If an exception occurs during the pipeline execution, it resets the Orchestrator instance,
        flushes the session, and renders an error page. If the pipeline runs successfully, it saves
        the session and selected modules. If the session indicates a comparison is being made, it
        saves the results to the database and redirects to the comparison page. Otherwise, it calls
        the parent class's form_valid method.

        Args:
            form (Form): The form instance that has just been validated.

        Returns:
            HttpResponse: The HTTP response to send back to the client.
        """

        orchestrator = Orchestrator.get_instance()
        orchestrator.get_configuration().update(
            event_types=form.cleaned_data["event_types"],
            locations=form.cleaned_data["locations"],
            activity_key=form.cleaned_data["activity_key"],
        )
        modules_list = (
            form.cleaned_data["modules_required"]
            + form.cleaned_data["modules_optional"]
        )
        orchestrator.reduce_modules_to(modules_list)
        try:
            orchestrator.run(view=self)
        except Exception as e:  # pylint: disable=broad-except
            orchestrator.reset_instance()
            self.request.session.flush()

            return render(
                self.request,
                "error_page.html",
                {"type": type(e).__name__, "error_traceback": traceback.format_exc()},
            )

        self.request.session.save()

        selected_modules = form.cleaned_data["modules_optional"]
        self.request.session["selected_modules"] = selected_modules

        if self.request.session.get("is_comparing") is True:
            orchestrator.save_results_to_db()

            return redirect(reverse_lazy("testing_comparison"))

        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to the view.

        If the request is an AJAX request, it returns a JSON response with the current progress
        and status of the extraction pipeline. If it's not an AJAX request, it resets the progress
        and status in the session and calls the parent class's get method.

        Args:
            request (HttpRequest): The request instance.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The HTTP response to send back to the client.
        """

        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
        if is_ajax:
            progress_information = {
                "progress": self.request.session.get("progress"),
                "status": self.request.session.get("status"),
            }
            return JsonResponse(progress_information)

        self.request.session["progress"] = 0
        self.request.session["status"] = None
        self.request.session.save()

        return super().get(request, *args, **kwargs)


class ResultView(generic.FormView):
    """View for displaying the result."""

    form_class = ResultForm
    template_name = "result.html"
    success_url = reverse_lazy("result")

    def get_form_kwargs(self):
        """Return the keyword arguments to instantiate the form."""
        kwargs = super().get_form_kwargs()
        orchestrator = Orchestrator.get_instance()
        kwargs["initial"] = {
            "activity_key": orchestrator.get_configuration().activity_key,
            "selected_modules": self.request.session.get("selected_modules"),
            "event_types": orchestrator.get_configuration().event_types,
            "locations": orchestrator.get_configuration().locations,
        }

        return kwargs

    def get_context_data(self, **kwargs):
        """
        Prepare the data for the result page.

        This method overrides the get_context_data method from the parent class. It retrieves the
        current instance of the Orchestrator and its configuration, builds the trace and event log
        dataframes based on the filter settings, and validates the form. It then updates the context
        with the form, journey, direct follow graph (dfg) images, and tables. Finally, it saves the
        trace and event log dataframes to the session and returns the context.

        Args:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict: The context data for the result page.
        """

        context = super().get_context_data(**kwargs)
        orchestrator = Orchestrator.get_instance()
        activity_key = orchestrator.get_configuration().activity_key
        filter_dict = {
            "event_type": orchestrator.get_configuration().event_types,
            "attribute_location": orchestrator.get_configuration().locations,
        }

        trace = self.build_trace_df(filter_dict)
        event_log = self.build_event_log_df(filter_dict, trace)

        form = self.get_form()
        form.is_valid()

        context.update(
            {
                "form": form,
                "journey": orchestrator.get_configuration().patient_journey,
                "dfg_img": utils.Conversion.create_dfg_from_df(
                    df=trace,
                    activity_key=activity_key,
                ),
                "trace_table": utils.Conversion.create_html_table_from_df(df=trace),
                "all_dfg_img": utils.Conversion.create_dfg_from_df(
                    df=event_log,
                    activity_key=activity_key,
                ),
                "event_log_table": utils.Conversion.create_html_table_from_df(
                    df=event_log
                ),
            }
        )

        self.request.session["trace"] = trace.to_json()
        self.request.session["event_log"] = event_log.to_json()

        return context

    @staticmethod
    def build_trace_df(filter_dict: Dict[str, List[str]]) -> pd.DataFrame:
        """Build the trace dataframe based on the filter settings."""
        trace_df = Orchestrator.get_instance().get_data()
        trace_df_filtered = utils.DataFrameUtilities.filter_dataframe(
            trace_df, filter_dict
        )
        trace_df_filtered = utils.DataFrameUtilities.delete_metrics_columns(
            trace_df_filtered
        )

        return trace_df_filtered

    @staticmethod
    def build_event_log_df(
        filter_dict: Dict[str, List[str]], trace: pd.DataFrame
    ) -> pd.DataFrame:
        """Build the event log dataframe based on the filter settings."""
        event_log_df = utils.DataFrameUtilities.get_events_df()

        if not event_log_df.empty:
            if not trace.empty:
                event_log_df = pd.concat(
                    [event_log_df, trace], ignore_index=True, axis="rows"
                )
            event_log_df = utils.DataFrameUtilities.filter_dataframe(
                event_log_df, filter_dict
            )
            event_log_df = utils.DataFrameUtilities.delete_metrics_columns(event_log_df)

        elif not trace.empty:
            event_log_df = trace

        return event_log_df

    def form_valid(self, form):
        """Update the Orchestrator's configuration with the filter settings from the form."""
        orchestrator = Orchestrator.get_instance()
        orchestrator.get_configuration().update(
            event_types=form.cleaned_data["event_types"],
            locations=form.cleaned_data["locations"],
            activity_key=form.cleaned_data["activity_key"],
        )
        modules_list = (
            form.cleaned_data["modules_required"]
            + form.cleaned_data["modules_optional"]
        )
        orchestrator.get_configuration().modules = modules_list

        return super().form_valid(form)


class SaveSuccessView(generic.TemplateView):
    """A Django view that displays a success message after saving the extraction results."""

    template_name = "save_success.html"

    def get_context_data(self, **kwargs):
        """Prepare and return the context data for the save success page."""
        context = super().get_context_data(**kwargs)
        orchestrator = Orchestrator.get_instance()
        orchestrator.save_results_to_db()

        return context


class DownloadXesResultView(DownloadXesView):
    """
    Download one or more XES files based on the types specified in POST request in the result view,
    bundled into a ZIP file if multiple files are selected.
    """

    @staticmethod
    def process_trace_type(request, trace_type):
        """Process and provide the XES files to be downloaded based on the trace type."""
        orchestrator = Orchestrator.get_instance()
        activity_key = orchestrator.get_configuration().activity_key

        if trace_type == "event_log":
            # Process event log data into XES format
            df = pd.read_json(request.session.get("event_log"))
            event_log_xes = utils.Conversion.dataframe_to_xes(
                df, name="event_log", activity_key=activity_key
            )
            return event_log_xes
        if trace_type == "trace":
            # Process trace data into XES format
            df = pd.read_json(request.session.get("trace"))
            trace_xes = utils.Conversion.dataframe_to_xes(
                df, name="trace", activity_key=activity_key
            )
            return trace_xes
        # Return None if the trace type is unrecognized

        return None
