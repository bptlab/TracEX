"""This file contains the views for the extraction app.
Some unused imports have to be made because of architectural requirement."""
# pylint: disable=unused-argument
import zipfile
import os
from tempfile import NamedTemporaryFile
import pandas as pd
from django.db.models import Q

from django.urls import reverse_lazy
from django.views import generic, View
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import redirect

from extraction.models import Cohort
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

        self.request.session["is_extracted"] = False
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
        single_trace_df = orchestrator.get_data()
        activity_key = orchestrator.get_configuration().activity_key

        filter_dict = {
            "event_type": orchestrator.get_configuration().event_types,
            "attribute_location": orchestrator.get_configuration().locations,
        }

        single_trace_df_filtered = utils.DataFrameUtilities.filter_dataframe(
            single_trace_df, filter_dict
        )

        # 3. Append the single journey dataframe to the all traces dataframe

        condition = Cohort.manager.get(
            pk=orchestrator.get_db_objects_id("cohort")
        ).condition  # get only those traces that belong to the same condition as the newly extracted trace
        all_traces_df = utils.DataFrameUtilities.get_events_df(
            Q(cohort__condition=condition)
        )
        if not all_traces_df.empty:
            utils.Conversion.align_df_datatypes(
                source_df=single_trace_df_filtered, target_df=all_traces_df
            )
            all_traces_df = pd.concat(
                [all_traces_df, single_trace_df_filtered],
                ignore_index=True,
                axis="rows",
            )
            all_traces_df_filtered = utils.DataFrameUtilities.filter_dataframe(
                all_traces_df, filter_dict
            )
        else:
            all_traces_df_filtered = single_trace_df_filtered

        # 4. Save all information in context to display on website
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
                    df=single_trace_df_filtered,
                    activity_key=activity_key,
                ),
                "single_trace_table": utils.Conversion.create_html_table_from_df(
                    single_trace_df_filtered
                ),
                "all_dfg_img": utils.Conversion.create_dfg_from_df(
                    df=all_traces_df_filtered,
                    activity_key=activity_key,
                ),
                "all_traces_table": utils.Conversion.create_html_table_from_df(
                    all_traces_df_filtered
                ),
            }
        )

        # 5 .Generate XES files
        single_trace_xes = utils.Conversion.dataframe_to_xes(
            single_trace_df_filtered, name="single_trace.xes", activity_key=activity_key
        )
        all_traces_xes = utils.Conversion.dataframe_to_xes(
            all_traces_df_filtered, name="all_traces.xes", activity_key=activity_key
        )

        # 6. Store XES in session for retrieval in DownloadXesView
        self.request.session["single_trace_xes"] = str(single_trace_xes)
        self.request.session["all_traces_xes"] = str(all_traces_xes)

        return context

    def form_valid(self, form):
        """Save the filter settings in the cache."""
        orchestrator = Orchestrator.get_instance()
        orchestrator.get_configuration().update(
            # This should not be necessary, unspecified values should be unchanged
            patient_journey=orchestrator.get_configuration().patient_journey,
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
        if trace_type == "all_traces":
            return request.session.get("all_traces_xes")
        if trace_type == "single_trace":
            return request.session.get("single_trace_xes")

        return None  # Return None for unrecognized trace type

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
