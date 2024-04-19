"""This file contains the views for the extraction app.
Some unused imports have to be made because of architectural requirement."""
# pylint: disable=unused-argument
import os
import pm4py
import pandas as pd

from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
from django.shortcuts import redirect

from tracex.logic import utils
from extraction.forms import JourneyForm, ResultForm, FilterForm
from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration


# necessary due to Windows error. see information for your os here:
# https://stackoverflow.com/questions/35064304/runtimeerror-make-sure-the-graphviz-executables-are-on-your-systems-path-aft
os.environ["PATH"] += os.pathsep + "C:/Program Files/Graphviz/bin/"

IS_TEST = False  # Controls the presentation mode of the pipeline, set to False if you want to run the pipeline


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
        """Run extraction pipeline and save the filter settings in the cache."""
        orchestrator = Orchestrator.get_instance()
        orchestrator.get_configuration().update(
            event_types=form.cleaned_data["event_types"],
            locations=form.cleaned_data["locations"],
        )
        orchestrator.run(view=self)
        single_trace_df = orchestrator.get_data()
        single_trace_df = utils.Conversion.prepare_df_for_xes_conversion(
            single_trace_df, orchestrator.get_configuration().activity_key
        )
        utils.Conversion.create_xes(
            utils.CSV_OUTPUT,
            name="single_trace",
            key=orchestrator.get_configuration().activity_key,
        )
        self.request.session["is_extracted"] = True
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
        event_types = orchestrator.get_configuration().event_types
        filter_dict = {
            "concept:name": event_types,
            "attribute_location": orchestrator.get_configuration().locations,
        }

        output_path_xes = f"{str(utils.output_path / 'single_trace')}_event_type.xes"
        single_trace_df = pm4py.read_xes(output_path_xes)

        # 2. Sort and filter the single journey dataframe
        single_trace_df = single_trace_df.sort_values(
            by="start_timestamp", inplace=False
        )
        single_trace_df_filtered = utils.DataFrameUtilities.filter_dataframe(
            single_trace_df, filter_dict
        )
        # 3. Append the single journey dataframe to the all traces dataframe

        # TODO: remove comment once cohort is implemented
        # condition = Cohort.manager.get(pk=orchestrator.get_db_objects_id("cohort")).condition
        # query = Q(cohort__condition=condition)
        all_traces_df = utils.DataFrameUtilities.get_events_df()
        if not all_traces_df.empty:
            all_traces_df = utils.Conversion.prepare_df_for_xes_conversion(
                all_traces_df, orchestrator.get_configuration().activity_key
            )
            utils.Conversion.align_df_datatypes(single_trace_df_filtered, all_traces_df)
            all_traces_df = pd.concat(
                [all_traces_df, single_trace_df_filtered],
                ignore_index=True,
                axis="rows",
            )
            all_traces_df = all_traces_df.groupby(
                "case:concept:name", group_keys=False, sort=False
            ).apply(lambda x: x.sort_values(by="start_timestamp", inplace=False))

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
                    }
                ),
                "journey": orchestrator.get_configuration().patient_journey,
                "dfg_img": utils.Conversion.create_dfg_from_df(
                    single_trace_df_filtered
                ),
                "xes_html": utils.Conversion.create_html_from_xes(
                    single_trace_df_filtered
                ).getvalue(),
                "all_dfg_img": utils.Conversion.create_dfg_from_df(
                    all_traces_df_filtered
                ),
                "all_xes_html": utils.Conversion.create_html_from_xes(
                    all_traces_df_filtered
                ).getvalue(),
            }
        )

        return context

    def form_valid(self, form):
        """Save the filter settings in the cache."""
        orchestrator = Orchestrator.get_instance()
        orchestrator.get_configuration().update(
            # This should not be necessary, unspecified values should be unchanged
            patient_journey=orchestrator.get_configuration().patient_journey,
            event_types=form.cleaned_data["event_types"],
            locations=form.cleaned_data["locations"],
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
