"""This file contains the views for the trace testing environment app."""
import traceback
from typing import Tuple, List

import pandas as pd

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView
from django.db.models import Q

from extraction.models import PatientJourney, Trace
from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration
from trace_comparator.comparator import compare_traces
from trace_comparator.forms import PatientJourneySelectForm
from tracex.logic.utils import DataFrameUtilities, Conversion


class TraceComparisonMixin(View):
    @staticmethod
    def get_first_and_last_trace(
        patient_journey_name: str,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Get the first and last trace of a patient journey from the database."""
        query_last_trace = Q(
            id=Trace.manager.filter(patient_journey__name=patient_journey_name)
            .latest("last_modified")
            .id
        )
        last_trace_df: pd.DataFrame = DataFrameUtilities.get_events_df(query_last_trace)
        query_first_trace = Q(
            id=Trace.manager.filter(patient_journey__name=patient_journey_name)
            .earliest("last_modified")
            .id
        )
        first_trace_df: pd.DataFrame = DataFrameUtilities.get_events_df(
            query_first_trace
        )

        return first_trace_df, last_trace_df


class TraceTestingOverviewView(FormView):
    """View for selecting a patient journey to use in the Trace Testing Environment."""

    form_class = PatientJourneySelectForm
    template_name = "testing_overview.html"
    success_url = reverse_lazy("journey_filter")

    def form_valid(self, form):
        """Pass selected journey to orchestrator and update session state to reflect, that the comparison has
        started."""
        selected_journey: str = form.cleaned_data["selected_patient_journey"]
        patient_journey_entry = PatientJourney.manager.get(name=selected_journey)
        configuration = ExtractionConfiguration(
            patient_journey=patient_journey_entry.patient_journey,
        )
        orchestrator = Orchestrator(configuration=configuration)
        orchestrator.set_db_objects_id("patient_journey", patient_journey_entry.id)
        self.request.session["patient_journey_name"] = selected_journey
        self.request.session["is_comparing"] = True

        return super().form_valid(form)


class TraceTestingComparisonView(TemplateView, TraceComparisonMixin):
    """View for comparing the pipeline output against the ground truth."""

    template_name = "testing_comparison.html"

    def get_context_data(self, **kwargs):
        """Prepare the latest trace of the selected patient journey that is available in the database for display."""
        context = super().get_context_data(**kwargs)
        patient_journey_name: str = self.request.session.get("patient_journey_name")
        patient_journey: str = PatientJourney.manager.get(
            name=patient_journey_name
        ).patient_journey
        query_last_trace = Q(
            id=Trace.manager.filter(patient_journey__name=patient_journey_name)
            .latest("last_modified")
            .id
        )
        pipeline_df: pd.DataFrame = DataFrameUtilities.get_events_df(query_last_trace)

        context.update(
            {
                "patient_journey_name": patient_journey_name,
                "patient_journey": patient_journey,
                "pipeline_output": Conversion.create_html_table_from_df(pipeline_df),
            }
        )

        return context

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

    def post(self, request):
        """Compare the newest trace of a patient journey against the ground truth and update session with results."""
        patient_journey_name: str = self.request.session.get("patient_journey_name")
        ground_truth_df, pipeline_df = self.get_first_and_last_trace(
            patient_journey_name
        )

        try:
            comparison_result_dict: dict = compare_traces(
                self, pipeline_df, ground_truth_df
            )
        except Exception:  # pylint: disable=broad-except
            self.request.session.flush()

            return render(
                self.request,
                "error_page.html",
                {"error_traceback": traceback.format_exc()},
            )

        request.session["comparison_result"] = comparison_result_dict

        return redirect("testing_result")


class TraceTestingResultView(TemplateView, TraceComparisonMixin):
    """View for displaying the comparison results."""

    template_name = "testing_result.html"

    @staticmethod
    def create_mapping_list(
        mapping: List[int], source_df: pd.DataFrame, target_df: pd.DataFrame
    ) -> List[List[str]]:
        """Create a list of mappings between two dataframes."""
        mapping_list = [
            [source_df["activity"][index], target_df["activity"][value]]
            for index, value in enumerate(mapping)
            if value != -1
        ]

        return mapping_list

    def get_context_data(self, **kwargs):
        """Convert comparison data into a format that can be displayed in the template."""
        context = super().get_context_data(**kwargs)
        patient_journey_name: str = self.request.session.get("patient_journey_name")
        comparison_result_dict: dict = self.request.session.get("comparison_result")

        ground_truth_df, pipeline_df = self.get_first_and_last_trace(
            patient_journey_name
        )

        (
            ground_truth_to_pipeline_df,
            missing_activities_df,
            pipeline_to_ground_truth_df,
            unexpected_activities_df,
            wrong_orders_df,
        ) = self.__create_result_dfs(
            comparison_result_dict, ground_truth_df, pipeline_df
        )

        context_update: dict = self.__build_context_update(
            comparison_result_dict,
            ground_truth_df,
            ground_truth_to_pipeline_df,
            missing_activities_df,
            patient_journey_name,
            pipeline_df,
            pipeline_to_ground_truth_df,
            unexpected_activities_df,
            wrong_orders_df,
        )
        context.update(context_update)

        return context

    @staticmethod
    def __build_context_update(
        comparison_result_dict,
        ground_truth_df,
        ground_truth_to_pipeline_df,
        missing_activities_df,
        patient_journey_name,
        pipeline_df,
        pipeline_to_ground_truth_df,
        unexpected_activities_df,
        wrong_orders_df,
    ):
        """Prepare a dictionary with the data needed to display the comparison results.

        All DataFrames are converted to HTML tables, the number of missing, unexpected and wrong activities are
        determined and all required results from 'comparison_results_dict' are added.
        """
        context_update = {
            "patient_journey_name": patient_journey_name,
            "patient_journey": PatientJourney.manager.get(
                name=patient_journey_name
            ).patient_journey,
            "pipeline_output": Conversion.create_html_table_from_df(pipeline_df),
            "ground_truth_output": Conversion.create_html_table_from_df(
                ground_truth_df
            ),
            "matching_percent_pipeline_to_ground_truth": comparison_result_dict.get(
                "matching_percent_pipeline_to_ground_truth"
            ),
            "matching_percent_ground_truth_to_pipeline": comparison_result_dict.get(
                "matching_percent_ground_truth_to_pipeline"
            ),
            "mapping_pipeline_to_ground_truth": pipeline_to_ground_truth_df.to_html(
                index=False
            ),
            "mapping_ground_truth_to_pipeline": ground_truth_to_pipeline_df.to_html(
                index=False
            ),
            "missing_activities": missing_activities_df.to_html(
                index=False, header=False
            ),
            "number_of_missing_activities": len(missing_activities_df),
            "unexpected_activities": unexpected_activities_df.to_html(
                index=False, header=False
            ),
            "number_of_unexpected_activities": len(unexpected_activities_df),
            "wrong_orders": wrong_orders_df.to_html(index=False),
            "number_of_wrong_orders": len(wrong_orders_df),
        }

        return context_update

    def __create_result_dfs(
        self,
        comparison_result_dict: dict,
        ground_truth_df: pd.DataFrame,
        pipeline_df: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Create DataFrames from the comparison results."""
        mapping_pipeline_to_ground_truth: List[int] = comparison_result_dict.get(
            "mapping_pipeline_to_ground_truth"
        )
        mapping_ground_truth_to_pipeline: List[int] = comparison_result_dict.get(
            "mapping_ground_truth_to_pipeline"
        )
        pipeline_to_ground_truth_list: List[List[str]] = self.create_mapping_list(
            mapping_pipeline_to_ground_truth, pipeline_df, ground_truth_df
        )
        ground_truth_to_pipeline_list: List[List[str]] = self.create_mapping_list(
            mapping_ground_truth_to_pipeline, ground_truth_df, pipeline_df
        )
        pipeline_to_ground_truth_df = pd.DataFrame(
            pipeline_to_ground_truth_list,
            columns=["Pipeline Activity", "Ground Truth Activity"],
        )
        ground_truth_to_pipeline_df = pd.DataFrame(
            ground_truth_to_pipeline_list,
            columns=["Ground Truth Activity", "Pipeline Activity"],
        )
        missing_activities_df = pd.DataFrame(
            comparison_result_dict.get("missing_activities")
        )
        unexpected_activities_df = pd.DataFrame(
            comparison_result_dict.get("unexpected_activities")
        )
        wrong_orders_df = pd.DataFrame(
            comparison_result_dict.get("wrong_orders"),
            columns=["Expected Preceding Activity", "Actual Preceding Activity"],
        )
        return (
            ground_truth_to_pipeline_df,
            missing_activities_df,
            pipeline_to_ground_truth_df,
            unexpected_activities_df,
            wrong_orders_df,
        )
