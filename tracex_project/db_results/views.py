"""This file contains the views for the database result app."""
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from db_results.forms import PatientJourneySelectForm
from django.db.models import Q

import plotly.graph_objects as go
from plotly.offline import plot

from extraction.models import Trace, PatientJourney
from tracex.logic.utils import DataFrameUtilities as dfu


class MetricsOverviewView(FormView):
    """View for selecting a patient journey for showing metrics."""

    form_class = PatientJourneySelectForm
    template_name = "metrics_pj_overview.html"
    success_url = reverse_lazy("metrics_dashboard")

    def form_valid(self, form):
        """Pass selected journey to orchestrator."""
        selected_journey = form.cleaned_data["selected_patient_journey"]
        self.request.session["patient_journey_name"] = selected_journey

        return super().form_valid(form)


class MetricsDashboardView(TemplateView):
    """View for displaying metrics."""

    template_name = "metrics_dashboard.html"

    def get_context_data(self, **kwargs):
        """Add relevant metrics to the context."""
        context = super().get_context_data(**kwargs)
        patient_journey_name = self.request.session["patient_journey_name"]
        query_last_trace = Q(
            id=Trace.manager.filter(patient_journey__name=patient_journey_name)
            .latest("last_modified")
            .id
        )
        trace_df = dfu.get_events_df(query_last_trace)

        relevance_counts = trace_df["activity_relevance"].value_counts()
        timestamp_correctness_counts = trace_df["timestamp_correctness"].value_counts()
        average_timestamp_correctness = round(
            trace_df["correctness_confidence"].mean(), 2
        )

        activity_relevance_pie_chart = self.create_pie_chart(relevance_counts)
        timestamp_correctness_pie_chart = self.create_pie_chart(
            timestamp_correctness_counts
        )
        activity_relevance_bar_chart = self.create_bar_chart(
            relevance_counts, "Activity Relevance", "Count"
        )
        timestamp_correctness_bar_chart = self.create_bar_chart(
            timestamp_correctness_counts, "Timestamp Correctness", "Count"
        )

        relevance_df = trace_df[["activity", "activity_relevance"]]
        relevance_df_styled = (
            relevance_df.style.set_table_attributes('class="dataframe"')
            .apply(self.color_relevance, axis=1)
            .hide()
        )
        timestamp_df = trace_df[
            [
                "activity",
                "start",
                "end",
                "timestamp_correctness",
                "correctness_confidence",
            ]
        ]
        timestamp_df = (
            timestamp_df.style.set_table_attributes('class="dataframe"')
            .apply(self.color_timestamp_correctness, axis=1)
            .hide()
        )

        context.update(
            {
                "patient_journey_name": patient_journey_name,
                "total_patient_journeys": PatientJourney.manager.count(),
                "total_traces": Trace.manager.count(),
                "total_activities": trace_df.shape[0],
                "traces_count": Trace.manager.filter(patient_journey__name=patient_journey_name).count(),
                "most_frequent_category": relevance_counts.index[0],
                "most_frequent_category_count": relevance_counts.values[0],
                "most_frequent_timestamp_correctness": timestamp_correctness_counts.index[
                    0
                ],
                "most_frequent_timestamp_correctness_count": timestamp_correctness_counts.values[
                    0
                ],
                "average_timestamp_correctness": average_timestamp_correctness,
                "relevance_df": relevance_df_styled.to_html(),
                "timestamp_df": timestamp_df.to_html(),
                "activity_relevance_pie_chart": activity_relevance_pie_chart,
                "timestamp_correctness_pie_chart": timestamp_correctness_pie_chart,
                "activity_relevance_bar_chart": activity_relevance_bar_chart,
                "timestamp_correctness_bar_chart": timestamp_correctness_bar_chart,
            }
        )
        return context

    @staticmethod
    def color_relevance(row):
        """Color the a row based on the activity relevance."""
        activity_relevance = row["activity_relevance"]
        if activity_relevance == "Moderate Relevance":
            return ["background-color: orange"] * len(row)
        if activity_relevance == "Low Relevance":
            return ["background-color: red"] * len(row)
        return [""] * len(row)

    @staticmethod
    def color_timestamp_correctness(row):
        """Color the a row based on the timestamp correctness confidence."""
        correctness_confidence = row["correctness_confidence"]
        if correctness_confidence >= 0.7 and correctness_confidence <= 0.8:
            return ["background-color: orange"] * len(row)
        if correctness_confidence < 0.7:
            return ["background-color: red"] * len(row)
        return [""] * len(row)

    @staticmethod
    def create_pie_chart(data):
        """Create a pie chart from the data."""
        return plot(
            go.Figure(
                data=[go.Pie(labels=data.index, values=data.values)],
                layout=go.Layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    autosize=True,
                ),
            ),
            output_type="div",
            include_plotlyjs=False,
            config={"displaylogo": False, "displayModeBar": False},
        )

    @staticmethod
    def create_bar_chart(data, x_title, y_title):
        """Create a bar chart from the data."""
        return plot(
            go.Figure(
                data=[go.Bar(x=data.index, y=data.values)],
                layout=go.Layout(
                    xaxis={"title": x_title, "gridcolor": "darkgrey"},
                    yaxis={"title": y_title, "gridcolor": "darkgrey"},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    autosize=True,
                ),
            ),
            output_type="div",
            include_plotlyjs=False,
            config={"displaylogo": False, "displayModeBar": False, "staticPlot": True},
        )
