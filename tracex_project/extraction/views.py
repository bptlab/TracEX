"""This file contains the views for the extraction app.
Some unused imports and variables have to be made because of architectural requirement."""
import traceback
# pylint: disable=unused-argument, unused-variable
import zipfile
import os
from tempfile import NamedTemporaryFile
import pandas as pd
from django.db.models import Q

from django.urls import reverse_lazy
from django.views import generic, View
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import redirect, render

from tracex.logic import utils, constants
from extraction.forms import (
    JourneyUploadForm,
    ResultForm,
    FilterForm,
    JourneySelectForm,
    EvaluationForm,
)
from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration
from extraction.models import PatientJourney


class JourneyInputSelectView(generic.TemplateView):
    """View for choosing if you want to upload a patient journey or select from the database."""

    template_name = "choose_input_method.html"


class JourneyUploadView(generic.CreateView):
    """View for uploading a patient journey."""

    form_class = JourneyUploadForm
    template_name = "upload_journey.html"

    def form_valid(self, form):
        """Save the uploaded journey in the cache."""
        uploaded_file = self.request.FILES.get("file")
        content = uploaded_file.read().decode("utf-8")
        form.instance.patient_journey = content
        response = super().form_valid(form)

        return response

    def get_success_url(self):
        """Return the success URL."""

        return reverse_lazy("journey_details", kwargs={"pk": self.object.id})


class JourneySelectView(generic.FormView):
    """View for selecting a patient journey from the database."""

    model = PatientJourney
    form_class = JourneySelectForm
    template_name = "select_journey.html"
    success_url = reverse_lazy("journey_details")

    def form_valid(self, form):
        """Pass selected journey to orchestrator."""
        selected_journey = form.cleaned_data["selected_patient_journey"]
        patient_journey_entry = PatientJourney.manager.get(name=selected_journey)

        return redirect("journey_details", pk=patient_journey_entry.pk)


class JourneyDetailView(generic.DetailView):
    """View for displaying the details of a patient journey."""

    model = PatientJourney
    template_name = "journey_details.html"

    def get_context_data(self, **kwargs):
        """Add patient journey to context."""
        context = super().get_context_data(**kwargs)
        patient_journey = self.get_object()
        context["patient_journey"] = patient_journey
        self.request.session["patient_journey_id"] = patient_journey.id

        return context

    def post(self, request, *args, **kwargs):
        """Redirect to the FilterView afterward."""
        patient_journey_id = self.request.session.get("patient_journey_id")
        patient_journey = PatientJourney.manager.get(pk=patient_journey_id)
        configuration = ExtractionConfiguration(
            patient_journey=patient_journey.patient_journey
        )
        orchestrator = Orchestrator(configuration)
        orchestrator.set_db_objects_id("patient_journey", patient_journey_id)

        return redirect("journey_filter")


class JourneyFilterView(generic.FormView):
    """View for selecting extraction results filter"""

    form_class = FilterForm
    template_name = "filter_journey.html"
    success_url = reverse_lazy("result")

    def get_context_data(self, **kwargs):
        """Add session variable to context."""
        context = super().get_context_data(**kwargs)
        context["is_comparing"] = self.request.session.get("is_comparing")

        return context

    def form_valid(self, form):
        """Run extraction pipeline and save the filter settings in the Orchestrator's configuration."""
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
        orchestrator.update_modules(modules_list)
        try:
            orchestrator.run(view=self)
        except Exception as e:  # pylint: disable=broad-except
            orchestrator.reset_instance()
            self.request.session.flush()

            return render(
                self.request,
                "error_page.html",
                {"type": type(e).__name__, "error_traceback": traceback.format_exc()}
            )

        self.request.session.save()

        selected_modules = form.cleaned_data["modules_optional"]
        self.request.session["selected_modules"] = selected_modules

        if self.request.session.get("is_comparing") is True:
            orchestrator.save_results_to_db()

            return redirect(reverse_lazy("testing_comparison"))

        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        """Return a JSON response with the current progress of the pipeline."""
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
        """Add the context to the form."""
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
        """Prepare the data for the result page."""
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
                    event_log
                ),
            }
        )

        self.request.session["trace"] = trace.to_json()
        self.request.session["event_log"] = event_log.to_json()

        return context

    @staticmethod
    def build_trace_df(filter_dict):
        """Build the trace df based on the filter settings."""
        trace_df = Orchestrator.get_instance().get_data()
        trace_df_filtered = utils.DataFrameUtilities.filter_dataframe(
            trace_df, filter_dict
        )

        return trace_df_filtered

    @staticmethod
    def build_event_log_df(filter_dict, trace):
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
        elif not trace.empty:
            event_log_df = trace

        return event_log_df

    def form_valid(self, form):
        """Save the filter settings in the cache."""
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
    """View for displaying the save success page."""

    template_name = "save_success.html"

    def get_context_data(self, **kwargs):
        """Prepare the data for the save success page."""
        context = super().get_context_data(**kwargs)
        orchestrator = Orchestrator.get_instance()
        orchestrator.save_results_to_db()

        return context


class DownloadXesView(View):
    """Download one or more XES files based on the types specified in POST request,
    bundled into a ZIP file if multiple."""

    def post(self, request, *args, **kwargs):
        """Processes a POST request to download specified trace types as XES files.
        Validates trace types and prepares the appropriate file response."""
        trace_types = self.get_trace_types(request)
        if not trace_types:
            return HttpResponse("No file type specified.", status=400)

        files_to_download = self.collect_files(request, trace_types)
        if (
                files_to_download is None
        ):  # Check for None explicitly to handle error scenario
            return HttpResponse("One or more files could not be found.", status=404)

        return self.prepare_response(files_to_download)

    @staticmethod
    def get_trace_types(request):
        """Retrieves a list of trace types from the POST data."""

        return request.POST.getlist("trace_type[]")

    def collect_files(self, request, trace_types):
        """Collects file for the specified trace types to download, checking for their existence."""
        files_to_download = []
        for trace_type in trace_types:
            file_path = self.process_trace_type(request, trace_type)
            if file_path:
                if os.path.exists(file_path):
                    files_to_download.append(file_path)
                else:
                    return None  # Return None if any file path is invalid

        return files_to_download

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

    def prepare_response(self, files_to_download):
        """Prepares the appropriate response based on the number of files to be downloaded."""
        if len(files_to_download) == 1:
            return self.single_file_response(files_to_download[0])

        return self.zip_files_response(files_to_download)

    # pylint: disable=consider-using-with
    @staticmethod
    def single_file_response(file_path):
        """Prepares a file if there is only a single XES file."""
        file = open(file_path, "rb")
        response = FileResponse(file, as_attachment=True)
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{os.path.basename(file_path)}"'

        return response

    @staticmethod
    def zip_files_response(files_to_download):
        """Prepares a zip file if there are multiple XES files using a temporary file."""
        temp_zip = NamedTemporaryFile(mode="w+b", suffix=".zip", delete=False)
        zipf = zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED)
        for file_path in files_to_download:
            zipf.write(file_path, arcname=os.path.basename(file_path))
        zipf.close()
        temp_zip_path = temp_zip.name
        temp_zip.close()

        file = open(temp_zip_path, "rb")
        response = FileResponse(file, as_attachment=True)
        response[
            "Content-Disposition"
        ] = 'attachment; filename="downloaded_xes_files.zip"'

        return response


class EvaluationView(generic.FormView):
    """View for displaying all extracted traces and DFG image with filter selection."""

    form_class = EvaluationForm
    template_name = "evaluation.html"
    success_url = reverse_lazy("evaluation")

    # TODO: Adjust get_context_data and form_valid so that the filters are applied to the data
    def get_context_data(self, **kwargs):
        """Prepare the data for the evaluation page."""
        context = super().get_context_data(**kwargs)
        config = self.initiate_evaluation_configuration()
        activity_key = config.get("activity_key")

        # Query the database to get all traces
        query_dict = self.request.session.get("query_dict")
        if query_dict is not None:
            query = self.create_query(query_dict)
            event_log_df = utils.DataFrameUtilities.get_events_df(query)
        else:
            event_log_df = utils.DataFrameUtilities.get_events_df()

        filter_dict = {
            "event_type": config.get("event_types"),
            "attribute_location": config.get("locations"),
        }
        if not event_log_df.empty:
            event_log_df = utils.DataFrameUtilities.filter_dataframe(
                event_log_df, filter_dict
            )
            context.update(
                {
                    "all_dfg_img": utils.Conversion.create_dfg_from_df(event_log_df, activity_key),
                    "event_log_table": utils.Conversion.create_html_table_from_df(event_log_df),
                }
            )

        context.update(
            {
                "form": EvaluationForm(initial=config),
            }
        )

        return context

    @staticmethod
    def create_query(query_dict):
        """Create a query object based on the given dictionary."""
        query = (
            Q(
                cohort__age__gte=query_dict.get("min_age"),
                cohort__age__lte=query_dict.get("max_age"),
            )
            if query_dict.get("min_age")
               and query_dict.get("max_age")
               and not query_dict.get("none_age")
            else Q()
        )
        if query_dict.get("none_age"):
            query |= Q(cohort__age__isnull=True)
        # Extend query for items of type list
        for key, value in query_dict.items():
            if isinstance(value, list) and len(value) > 0:
                # include entries where the respective attribute is missing
                if "None" in value:
                    query &= Q(**{f"cohort__{key}__isnull": True}) | Q(
                        **{f"cohort__{key}__in": value}
                    )
                else:
                    query &= Q(**{f"cohort__{key}__in": value})

        return query

    def form_valid(self, form):
        """Save the filter settings in the cache and apply them to the dataframe."""

        self.request.session["filter_settings"] = form.cleaned_data

        query_dict = {
            "gender": form.cleaned_data["gender"],
            "condition": form.cleaned_data["condition"],
            "preexisting_condition": form.cleaned_data["preexisting_condition"],
            "min_age": form.cleaned_data["min_age"],
            "max_age": form.cleaned_data["max_age"],
            "none_age": form.cleaned_data["none_age"],
            "origin": form.cleaned_data["origin"],
        }
        self.request.session["query_dict"] = query_dict

        return super().form_valid(form)

    def initiate_evaluation_configuration(self):
        """Initialize form with default values if no filter settings are present."""

        config = self.request.session.get("filter_settings")
        if config is None:
            config = {
                "event_types": [event_type[0] for event_type in constants.EVENT_TYPES],
                "locations": [location[0] for location in constants.LOCATIONS],
                "activity_key": constants.ACTIVITY_KEYS[0][0],
            }

        return config
