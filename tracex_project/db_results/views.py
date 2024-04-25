"""This file contains the views for the database result app."""
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from db_results.forms import PatientJourneySelectForm
from extraction.models import Trace

import plotly.graph_objects as go
from plotly.offline import plot

from tracex.logic.utils import DataFrameUtilities as dfu
from django.db.models import Q


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
    """View for comparing the pipeline output against the ground truth."""

    template_name = "metrics_dashboard.html"

    def get_context_data(self, **kwargs):
        """Add the plots to the context."""
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
        timestamp_df = trace_df[
            [
                "activity",
                "start",
                "end",
                "timestamp_correctness",
                "correctness_confidence",
            ]
        ]

        context.update(
            {
                "most_frequent_category": relevance_counts.index[0],
                "most_frequent_category_count": relevance_counts.values[0],
                "most_frequent_timestamp_correctness": timestamp_correctness_counts.index[
                    0
                ],
                "most_frequent_timestamp_correctness_count": timestamp_correctness_counts.values[
                    0
                ],
                "average_timestamp_correctness": average_timestamp_correctness,
                "relevance_df": relevance_df.to_html(),
                "timestamp_df": timestamp_df.to_html(),
                "activity_relevance_pie_chart": activity_relevance_pie_chart,
                "timestamp_correctness_pie_chart": timestamp_correctness_pie_chart,
                "activity_relevance_bar_chart": activity_relevance_bar_chart,
                "timestamp_correctness_bar_chart": timestamp_correctness_bar_chart,
            }
        )
        return context

    def create_pie_chart(self, data):
        return plot(
            go.Figure(
                data=[go.Pie(labels=data.index, values=data.values)],
                layout=go.Layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
                ),
            ),
            output_type="div",
            include_plotlyjs=True,
            config={"displaylogo": False, "displayModeBar": False},
        )

    def create_bar_chart(self, data, x_title, y_title):
        return plot(
            go.Figure(
                data=[go.Bar(x=data.index, y=data.values)],
                layout=go.Layout(
                    xaxis=dict(title=x_title),
                    yaxis=dict(title=y_title),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    autosize=True,
                ),
            ),
            output_type="div",
            include_plotlyjs=True,
            config={"displaylogo": False, "displayModeBar": False, "staticPlot": True},
        )
