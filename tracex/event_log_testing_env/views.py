"""This file contains the views for the event log testing environment app."""
from django.views.generic import FormView, TemplateView, View
from django.urls import reverse_lazy
from .forms import PatientJourneySelectForm
from extraction.models import PatientJourney
from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration
from . import comparator
from tracex.logic import utils
from django.shortcuts import redirect
import pandas as pd


class EventLogTestingOverviewView(FormView):
    form_class = PatientJourneySelectForm
    template_name = "testing_overview.html"
    success_url = reverse_lazy("journey_filter")

    def form_valid(self, form):
        selected_journey = form.cleaned_data["selected_patient_journey"]
        patient_journey_entry = PatientJourney.manager.get(name=selected_journey)
        configuration = ExtractionConfiguration(
            patient_journey=patient_journey_entry.patient_journey,
        )
        orchestrator = Orchestrator(configuration=configuration)
        orchestrator.set_db_id_objects("patient_journey", patient_journey_entry.id)
        self.request.session["patient_journey_name"] = selected_journey
        self.request.session["is_comparing"] = True

        return super().form_valid(form)


class EventLogTestingComparisonView(TemplateView):
    template_name = "testing_comparison.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_journey_name = self.request.session.get("patient_journey_name")
        patient_journey = PatientJourney.manager.get(
            name=patient_journey_name
        ).patient_journey
        pipeline_output_df = utils.DataFrameUtilities.get_events_df(
            patient_journey_name=patient_journey_name,
            trace_position="last",
        )
        context["patient_journey_name"] = patient_journey_name
        context["patient_journey"] = patient_journey
        context["xes_pipeline_output"] = utils.Conversion.create_html_from_xes(
            pipeline_output_df
        ).getvalue()

        return context

    def post(self, request, *args, **kwargs):
        """Comparing a generated trace of a patient journey against the ground truth."""
        patient_journey_name = self.request.session.get("patient_journey_name")
        pipeline_output_df = utils.DataFrameUtilities.get_events_df(
            patient_journey_name=patient_journey_name,
            trace_position="last",
        )
        pipeline_output_df = utils.DataFrameUtilities.sort_dataframe(pipeline_output_df)
        ground_truth_df = utils.DataFrameUtilities.get_events_df(
            patient_journey_name=patient_journey_name,
            trace_position="first",
        )
        ground_truth_df = utils.DataFrameUtilities.sort_dataframe(ground_truth_df)

        comparison_result_dict = comparator.execute(
            self, pipeline_output_df, ground_truth_df
        )

        request.session["comparison_result"] = comparison_result_dict

        return redirect("testing_result")


class EventLogTestingResultView(TemplateView):
    template_name = "testing_result.html"

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        patient_journey_name = self.request.session.get("patient_journey_name")
        context["patient_journey_name"] = patient_journey_name
        context["patient_journey"] = PatientJourney.manager.get(
            name=patient_journey_name
        ).patient_journey
        pipeline_output_df = utils.DataFrameUtilities.get_events_df(
            patient_journey_name=patient_journey_name,
            trace_position="last",
        )
        pipeline_output_df = utils.DataFrameUtilities.sort_dataframe(pipeline_output_df)
        ground_truth_df = utils.DataFrameUtilities.get_events_df(
            patient_journey_name=patient_journey_name,
            trace_position="first",
        )
        ground_truth_df = utils.DataFrameUtilities.sort_dataframe(ground_truth_df)
        context["xes_pipeline_output"] = utils.Conversion.create_html_from_xes(
            request.get("pipeline_output_df")
        ).getvalue()
        context["xes_ground_truth"] = utils.Conversion.create_html_from_xes(
            request.get("ground_truth_df")
        ).getvalue()

        comparison_result_dict = request.session.get("comparison_result")

        context["matching_percent_pipeline_to_ground_truth"] = comparison_result_dict[
            "matching_percent_pipeline_to_ground_truth"
        ]
        context["matching_percent_ground_truth_to_pipeline"] = comparison_result_dict[
            "matching_percent_ground_truth_to_pipeline"
        ]

        mapping_data_to_ground_truth = comparison_result_dict[
            "mapping_data_to_ground_truth"
        ]
        mapping_ground_truth_to_data = comparison_result_dict[
            "mapping_ground_truth_to_data"
        ]

        data_to_ground_truth_list = []
        ground_truth_to_data_list = []

        for index, value in enumerate(mapping_data_to_ground_truth):
            if value != -1:
                data_to_ground_truth_list.append(
                    [
                        pipeline_output_df["activity"][index],
                        ground_truth_df["activity"][value],
                    ]
                )

        for index, value in enumerate(mapping_ground_truth_to_data):
            if value != -1:
                ground_truth_to_data_list.append(
                    [
                        ground_truth_df["activity"][index],
                        pipeline_output_df["activity"][value],
                    ]
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
            comparison_result_dict["missing_activities"], columns=["Missing Activities"]
        )
        unexpected_activities_df = pd.DataFrame(
            comparison_result_dict["unexpected_activities"],
            columns=["Unexpected Activities"],
        )
        wrong_orders_df = pd.DataFrame(
            comparison_result_dict["wrong_orders"], columns=["Wrong Orders"]
        )

        context["mapping_data_to_ground_truth_df"] = data_to_ground_truth_df.to_html()
        context["mapping_ground_truth_to_data_df"] = ground_truth_to_data_df.to_html()

        context["number_of_missing_activities"] = comparison_result_dict[
            "number_of_missing_activities"
        ]
        context["missing_activities"] = missing_activities_df.to_html()
        context["number_of_unexpected_activities"] = comparison_result_dict[
            "number_of_unexpected_activities"
        ]
        context["unexpected_activities"] = unexpected_activities_df.to_html()
        context["number_of_wrong_orders"] = comparison_result_dict[
            "number_of_wrong_orders"
        ]
        context["wrong_orders"] = wrong_orders_df.to_html()

        return self.render_to_response(context)
