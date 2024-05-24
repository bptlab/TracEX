"""This file contains the views for the database result app."""
from typing import Tuple, List, Dict

import pandas as pd
import plotly.graph_objects as go
from db_results.forms import PatientJourneySelectForm, EvaluationForm
from django.db.models import Q
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from extraction.models import Trace, PatientJourney, Cohort
from plotly.offline import plot
from tracex.logic import utils as u
from tracex.logic.constants import ACTIVITY_KEYS, EVENT_TYPES, LOCATIONS
from tracex.views import DownloadXesView


class DbResultsOverviewView(TemplateView):
    """View for the database results overview."""

    template_name = "db_results_overview.html"

    def get_context_data(self, **kwargs):
        """Retrieve and return the base context data for the view, flushing the session data."""
        context = super().get_context_data(**kwargs)
        self.request.session.flush()

        return context


class MetricsOverviewView(FormView):
    """View for selecting a patient journey for showing metrics."""

    form_class = PatientJourneySelectForm
    template_name = "metrics_pj_overview.html"
    success_url = reverse_lazy("metrics_dashboard")

    def form_valid(self, form):
        """Process a valid form, save the selected journey in the session, and continue with form handling."""
        selected_journey = form.cleaned_data["selected_patient_journey"]
        self.request.session["patient_journey_name"] = selected_journey

        return super().form_valid(form)


class MetricsDashboardView(TemplateView):
    """View for displaying metrics."""

    template_name = "metrics_dashboard.html"

    def get_context_data(self, **kwargs):
        """
        Extend the existing context with additional metrics relevant to the patient journey.

        This method retrieves the patient journey name from the session, fetches the corresponding
        data frame, and updates the context object with various metrics and visualizations such as
        counts, charts, and data tables related to the patient journey.
        """

        context = super().get_context_data(**kwargs)
        trace_df = self.get_latest_trace_df()

        self.update_context_with_counts(context, trace_df)
        self.update_context_with_charts(context, trace_df)
        self.update_context_with_data_tables(context, trace_df)

        return context

    def get_latest_trace_df(self) -> pd.DataFrame:
        """
        Fetch the DataFrame for the latest trace of a specific patient journey stored in the session.

        This method constructs a query to fetch the ID of the latest trace entry related to a
        patient journey. It considers only those entries where activity relevance, timestamp correctness,
        and correctness confidence metrics are not null. It then retrieves the DataFrame for these
        events.
        """
        patient_journey_name = self.request.session["patient_journey_name"]

        query_last_trace = Q(
            id=Trace.manager.filter(
                patient_journey__name=patient_journey_name,
                events__metrics__activity_relevance__isnull=False,
                events__metrics__timestamp_correctness__isnull=False,
                events__metrics__correctness_confidence__isnull=False,
            )
            .latest("last_modified")
            .id
        )
        return u.DataFrameUtilities.get_events_df(query_last_trace)

    def update_context_with_counts(self, context, trace_df: pd.DataFrame):
        """Update the given context dictionary with count statistics related to patient journeys and traces."""
        patient_journey_name = self.request.session["patient_journey_name"]

        context.update({
            "patient_journey_name": patient_journey_name,
            "total_patient_journeys": PatientJourney.manager.count(),
            "total_traces": Trace.manager.count(),
            "total_activities": trace_df.shape[0],
            "traces_count": Trace.manager.filter(patient_journey__name=patient_journey_name).count()
        })

    def update_context_with_charts(self, context, trace_df: pd.DataFrame):
        """Update the context dictionary with chart visualizations."""
        relevance_counts = trace_df["activity_relevance"].value_counts()
        timestamp_correctness_counts = trace_df["timestamp_correctness"].value_counts()

        context.update({
            "activity_relevance_pie_chart": self.create_pie_chart(relevance_counts),
            "timestamp_correctness_pie_chart": self.create_pie_chart(timestamp_correctness_counts),
            "activity_relevance_bar_chart": self.create_bar_chart(relevance_counts, "Activity Relevance", "Count"),
            "timestamp_correctness_bar_chart": self.create_bar_chart(timestamp_correctness_counts,
                                                                     "Timestamp Correctness", "Count"),
            "most_frequent_category": relevance_counts.index[0],
            "most_frequent_category_count": relevance_counts.values[0],
            "most_frequent_timestamp_correctness": timestamp_correctness_counts.index[0],
            "most_frequent_timestamp_correctness_count": timestamp_correctness_counts.values[0],
            "average_timestamp_correctness": round(trace_df["correctness_confidence"].mean(), 2)
        })

    def update_context_with_data_tables(self, context, trace_df: pd.DataFrame):
        """Format trace data into styled HTML tables and add them to the context."""

        # Apply renaming, styling, and convert to HTML, then update the context
        relevance_columns = ["activity", "activity_relevance"]
        timestamp_columns = ["activity", "time:timestamp", "time:end_timestamp", "timestamp_correctness",
                             "correctness_confidence"]

        relevance_df = trace_df[relevance_columns]
        relevance_df = u.Conversion.rename_columns(relevance_df)
        relevance_styled = relevance_df.style.set_table_attributes('class="dataframe"').apply(self.color_relevance,
                                                                                              axis=1).hide().to_html()

        timestamp_df = trace_df[timestamp_columns]
        timestamp_df = u.Conversion.rename_columns(timestamp_df)
        timestamp_styled = timestamp_df.style.set_table_attributes('class="dataframe"').apply(
            self.color_timestamp_correctness, axis=1).hide().to_html()

        context.update({
            "relevance_df": relevance_styled,
            "timestamp_df": timestamp_styled
        })

    @staticmethod
    def color_relevance(row: pd.Series) -> List[str]:
        """Apply background color styling to a DataFrame row based on the activity relevance."""
        activity_relevance = row["Activity Relevance"]
        if activity_relevance == "Moderate Relevance":
            return ["background-color: orange"] * len(row)

        if activity_relevance == "Low Relevance":
            return ["background-color: red"] * len(row)

        return [""] * len(row)

    @staticmethod
    def color_timestamp_correctness(row: pd.Series) -> List[str]:
        """Apply background color styling to cells in a DataFrame row based on timestamp correctness and confidence."""
        correctness_confidence = row["Correctness Confidence"]
        confidence_index = row.index.get_loc("Correctness Confidence")
        timestamp_correctness = row["Timestamp Correctness"]
        styles = [""] * len(row)

        low_confidence_threshold = 0.7
        high_confidence_threshold = 0.8

        if timestamp_correctness is False:
            styles = ["background-color: tan"] * len(row)

        if (
                low_confidence_threshold
                <= correctness_confidence
                <= high_confidence_threshold
        ):
            styles[confidence_index] = "background-color: orange"
        elif correctness_confidence < low_confidence_threshold:
            styles[confidence_index] = "background-color: red"

        return styles

    @staticmethod
    def create_pie_chart(data: pd.Series) -> str:
        """Create a pie chart from the provided data using Plotly."""
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
            config={"displaylogo": False, "displayModeBar": False, "showTips": False},
        )

    @staticmethod
    def create_bar_chart(data: pd.Series, x_title: str, y_title: str) -> str:
        """Create a bar chart from the provided data using Plotly."""
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
            config={
                "displaylogo": False,
                "displayModeBar": False,
                "staticPlot": True,
                "showTips": False,
            },
        )


class EvaluationView(FormView):
    """
    View for displaying all extracted traces and DFG images with filter selection options.
    """

    form_class = EvaluationForm
    template_name = "evaluation.html"
    success_url = reverse_lazy("evaluation")

    def get_context_data(self, **kwargs):
        """
        Prepare and enrich the context data for rendering the evaluation page.

        This method initializes the filter settings, retrieves trace and event log data based on the session's
        current configuration, and processes this data to update the context with visualizations and HTML tables
        necessary for user interaction.
        """
        context = super().get_context_data(**kwargs)
        self.initialize_filter_settings()
        filter_settings = self.request.session.get("filter_settings")

        traces, event_log_df = self.get_traces_and_events()
        cohorts_df = self.get_cohorts_data(traces)

        if not event_log_df.empty:
            event_log_df = self.filter_and_cleanup_event_log(event_log_df, filter_settings)
            context.update(self.generate_dfg_and_tables(event_log_df, cohorts_df, filter_settings))

        context.update({"form": EvaluationForm(initial=filter_settings)})
        self.request.session["event_log"] = event_log_df.to_json()
        return context

    def get_traces_and_events(self) -> Tuple[QuerySet, pd.DataFrame]:
        """
        Fetch trace data and corresponding event logs based on the current session configuration.

        Retrieves traces and associated event data using either a specific query from session data or all available
        data if no specific query is defined.

        Returns:
            tuple: A pair containing a QuerySet of traces and a DataFrame of event logs.
        """
        query_dict = self.request.session.get("query_dict")
        if query_dict:
            query = self.create_query(query_dict)
            event_log_df = u.DataFrameUtilities.get_events_df(query)
            traces = Trace.manager.filter(query)
        else:
            event_log_df = u.DataFrameUtilities.get_events_df()
            traces = Trace.manager.all()
        return traces, event_log_df

    @staticmethod
    def get_cohorts_data(traces: QuerySet) -> pd.DataFrame:
        """Extract and format cohort data from given traces for further processing and visualization."""
        cohorts = Cohort.manager.filter(trace__in=traces)
        cohorts_data = list(cohorts.values("trace", "age", "sex", "origin", "condition", "preexisting_condition"))
        cohorts_df = pd.DataFrame(cohorts_data)
        if not cohorts_df.empty:
            cohorts_df["age"] = cohorts_df["age"].astype(pd.Int64Dtype())
        return cohorts_df

    @staticmethod
    def filter_and_cleanup_event_log(event_log_df: pd.DataFrame, filter_settings: dict) -> pd.DataFrame:
        """Apply user-defined filters to the event log data and clean up unnecessary columns."""
        filter_dict = {
            "event_type": filter_settings.get("event_types"),
            "attribute_location": filter_settings.get("locations"),
        }
        event_log_df = u.DataFrameUtilities.filter_dataframe(event_log_df, filter_dict)
        event_log_df = event_log_df.drop(
            columns=["activity_relevance", "timestamp_correctness", "correctness_confidence"])
        return event_log_df

    @staticmethod
    def generate_dfg_and_tables(event_log_df: pd.DataFrame, cohorts_df: pd.DataFrame,
                                filter_settings: dict) -> dict:
        """Generate visualizations and HTML tables for the provided event log and cohort data."""
        activity_key = filter_settings.get("activity_key")
        return {
            "all_dfg_img": u.Conversion.create_dfg_from_df(event_log_df, activity_key),
            "event_log_table": u.Conversion.create_html_table_from_df(event_log_df),
            "cohorts_table": u.Conversion.create_html_table_from_df(cohorts_df),
        }

    @staticmethod
    def create_query(query_dict: Dict[str, any]) -> Q:
        """Construct a database query from a dictionary of filter criteria."""
        query = Q(
            cohort__age__gte=query_dict.get("min_age"),
            cohort__age__lte=query_dict.get("max_age"),
        )
        if query_dict.get("none_age"):
            query |= Q(cohort__age__isnull=True)
        for key, value in query_dict.items():
            if isinstance(value, list) and len(value) > 0:
                query &= Q(**{f"cohort__{key}__in": value}) | Q(**{f"cohort__{key}__isnull": True})
        return query

    def form_valid(self, form):
        """Handle the submission of a valid form, updating session data with the provided filter settings."""
        self.request.session["filter_settings"] = form.cleaned_data

        query_dict = {
            "sex": form.cleaned_data["sex"],
            "condition": form.cleaned_data["condition"],
            "preexisting_condition": form.cleaned_data["preexisting_condition"],
            "min_age": form.cleaned_data["min_age"],
            "max_age": form.cleaned_data["max_age"],
            "none_age": form.cleaned_data["none_age"],
            "origin": form.cleaned_data["origin"],
        }
        self.request.session["query_dict"] = query_dict

        return super().form_valid(form)

    def initialize_filter_settings(self):
        """Initialize default filter settings in the session if they are not already set."""
        if "filter_settings" not in self.request.session:
            defaults = {
                "event_types": [event_type[0] for event_type in EVENT_TYPES],
                "locations": [location[0] for location in LOCATIONS],
                "activity_key": ACTIVITY_KEYS[0][0],
            }
            self.request.session["filter_settings"] = defaults


class DownloadXesEvaluationView(DownloadXesView):
    """View to download evaluation data in XES format based on the event log stored in the session."""

    @staticmethod
    def process_trace_type(request, trace_type: str):
        """Process and provide the XES files to be downloaded based on the trace type."""
        configuration = request.session.get("filter_settings")
        activity_key = configuration.get("activity_key")

        if trace_type == "event_log":
            df = pd.read_json(request.session.get("event_log"))

            if df.empty:
                return None

            event_log_xes = u.Conversion.dataframe_to_xes(
                df, name="event_log", activity_key=activity_key
            )
            return event_log_xes

        return None
