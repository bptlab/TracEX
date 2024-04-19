"""This file contains the views for the trace testing environment app."""
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.db.models import Q, Max, Min

from extraction.models import PatientJourney, Trace
from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration
from trace_comparator.comparator import compare_traces
from trace_comparator.forms import PatientJourneySelectForm
from tracex.logic.utils import DataFrameUtilities as dfu

import pandas as pd


class TraceTestingOverviewView(FormView):
    """View for selecting a patient journey for testing."""

    form_class = PatientJourneySelectForm
    template_name = "testing_overview.html"
    success_url = reverse_lazy("journey_filter")

    def form_valid(self, form):
        """Pass selected journey to orchestrator."""
        selected_journey = form.cleaned_data["selected_patient_journey"]
        patient_journey_entry = PatientJourney.manager.get(name=selected_journey)
        configuration = ExtractionConfiguration(
            patient_journey=patient_journey_entry.patient_journey,
        )
        orchestrator = Orchestrator(configuration=configuration)
        orchestrator.set_db_objects_id("patient_journey", patient_journey_entry.id)
        self.request.session["patient_journey_name"] = selected_journey
        self.request.session["is_comparing"] = True

        return super().form_valid(form)


class TraceTestingComparisonView(TemplateView):
    """View for comparing the pipeline output against the ground truth."""

    template_name = "testing_comparison.html"

    def get_context_data(self, **kwargs):
        """Preparing displaying extraction pipeline results"""
        context = super().get_context_data(**kwargs)
        patient_journey_name = self.request.session.get("patient_journey_name")
        patient_journey = PatientJourney.manager.get(
            name=patient_journey_name
        ).patient_journey
        query_last_trace = Q(
            id=Trace.manager.filter(
                patient_journey__name=patient_journey_name
            ).aggregate(Max("id"))["id__max"]
        )
        pipeline_df = dfu.get_events_df(query_last_trace)

        context.update(
            {
                "patient_journey_name": patient_journey_name,
                "patient_journey": patient_journey,
                "pipeline_output": pipeline_df.to_html(index=False),
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

        return super().get(request, *args, **kwargs)

    def post(self, request):
        """Comparing a generated trace of a patient journey against the ground truth."""
        patient_journey_name = self.request.session.get("patient_journey_name")
        query_last_trace = Q(
            id=Trace.manager.filter(
                patient_journey__name=patient_journey_name
            ).aggregate(Max("id"))["id__max"]
        )
        pipeline_df = dfu.get_events_df(query_last_trace)
        query_first_trace = Q(
            id=Trace.manager.filter(
                patient_journey__name=patient_journey_name
            ).aggregate(Min("id"))["id__min"]
        )
        ground_truth_df = dfu.get_events_df(query_first_trace)

        comparison_result_dict = compare_traces(self, pipeline_df, ground_truth_df)

        request.session["comparison_result"] = comparison_result_dict

        return redirect("testing_result")


class TraceTestingResultView(TemplateView):
    """View for displaying the comparison results."""

    template_name = "testing_result.html"

    def create_mapping_list(self, mapping, source_df, target_df):
        """Create a list of mappings between two dataframes."""
        mapping_list = [
            [source_df["activity"][index], target_df["activity"][value]]
            for index, value in enumerate(mapping)
            if value != -1
        ]
        return mapping_list

    def get_context_data(self, **kwargs):
        """Prepare the data for the trace testing results page."""
        context = super().get_context_data(**kwargs)
        patient_journey_name = self.request.session.get("patient_journey_name")
        query_last_trace = Q(
            id=Trace.manager.filter(
                patient_journey__name=patient_journey_name
            ).aggregate(Max("id"))["id__max"]
        )
        pipeline_df = dfu.get_events_df(query_last_trace)
        query_first_trace = Q(
            id=Trace.manager.filter(
                patient_journey__name=patient_journey_name
            ).aggregate(Min("id"))["id__min"]
        )
        ground_truth_df = dfu.get_events_df(query_first_trace)

        comparison_result_dict = self.request.session.get("comparison_result")
        mapping_data_to_ground_truth = comparison_result_dict.get(
            "mapping_data_to_ground_truth"
        )
        mapping_ground_truth_to_data = comparison_result_dict.get(
            "mapping_ground_truth_to_data"
        )

        data_to_ground_truth_list = self.create_mapping_list(
            mapping_data_to_ground_truth, pipeline_df, ground_truth_df
        )
        ground_truth_to_data_list = self.create_mapping_list(
            mapping_ground_truth_to_data, ground_truth_df, pipeline_df
        )

        data_to_ground_truth_df = pd.DataFrame(
            data_to_ground_truth_list,
            columns=["Pipeline Activity", "Ground Truth Activity"],
        )
        ground_truth_to_data_df = pd.DataFrame(
            ground_truth_to_data_list,
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

        context.update(
            {
                "patient_journey_name": patient_journey_name,
                "patient_journey": PatientJourney.manager.get(
                    name=patient_journey_name
                ).patient_journey,
                "pipeline_output": pipeline_df.to_html(index=False),
                "ground_truth_output": ground_truth_df.to_html(index=False),
                "mapping_data_to_ground_truth": data_to_ground_truth_df.to_html(
                    index=False
                ),
                "mapping_ground_truth_to_data": ground_truth_to_data_df.to_html(
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
        )

        return context
