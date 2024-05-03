"""This file contains the views for the extraction app.
Some unused imports have to be made because of architectural requirement."""
# pylint: disable=unused-argument
import zipfile
import os
from tempfile import NamedTemporaryFile
import pandas as pd

from django.urls import reverse_lazy
from django.views import generic, View
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import redirect

from tracex.logic import utils
from extraction.forms import JourneyForm, ResultForm, FilterForm
from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration

# necessary due to Windows error. see information for your os here:
# https://stackoverflow.com/questions/35064304/runtimeerror-make-sure-the-graphviz-executables-are-on-your-systems-path-aft
os.environ["PATH"] += os.pathsep + "C:/Program Files/Graphviz/bin/"


class JourneyInputView(generic.CreateView):
    """View for uploading a patient journey."""

    form_class = JourneyForm
    template_name = "upload_journey.html"
    success_url = reverse_lazy("journey_filter")

    def form_valid(self, form):
        """Save the uploaded journey in the cache."""
        uploaded_file = self.request.FILES.get("file")
        content = uploaded_file.read().decode("utf-8")
        form.instance.patient_journey = content

        response = super().form_valid(form)
        configuration = ExtractionConfiguration(patient_journey=content)
        orchestrator = Orchestrator(configuration)
        orchestrator.set_db_objects_id("patient_journey", self.object.id)

        return response


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
        orchestrator.run(view=self)
        self.request.session.save()

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

        context.update(
            {
                "form": ResultForm(
                    initial={
                        "event_types": orchestrator.get_configuration().event_types,
                        "locations": orchestrator.get_configuration().locations,
                        "activity_key": activity_key,
                    }
                ),
                "journey": orchestrator.get_configuration().patient_journey,
                "dfg_img": utils.Conversion.create_dfg_from_df(
                    df=trace,
                    activity_key=activity_key,
                ),
                "trace_table": utils.Conversion.create_html_table_from_df(trace),
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
