"""This file contains the views for the database result app."""
import pandas as pd
import plotly.graph_objects as go

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from plotly.offline import plot
from tracex.logic import utils as u
from tracex.logic.constants import ACTIVITY_KEYS, EVENT_TYPES, LOCATIONS
from tracex.views import DownloadXesView
from db_results.forms import PatientJourneySelectForm, EvaluationForm
from extraction.models import Trace, PatientJourney, Cohort


class DbResultsOverviewView(TemplateView):
    """View for the database results overview."""

    template_name = "db_results_overview.html"


class MetricsOverviewView(FormView):
    """View for selecting a patient journey for showing metrics."""

    form_class = PatientJourneySelectForm
    template_name = "metrics_pj_overview.html"
    success_url = reverse_lazy("metrics_dashboard")

    def form_valid(self, form):
        """Save selected journey in session."""
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
            id=Trace.manager.filter(
                patient_journey__name=patient_journey_name,
                events__metrics__activity_relevance__isnull=False,
                events__metrics__timestamp_correctness__isnull=False,
                events__metrics__correctness_confidence__isnull=False,
            )
            .latest("last_modified")
            .id
        )
        trace_df = u.DataFrameUtilities.get_events_df(query_last_trace)

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
        relevance_df = u.Conversion.rename_columns(relevance_df)
        relevance_df_styled = (
            relevance_df.style.set_table_attributes('class="dataframe"')
            .apply(self.color_relevance, axis=1)
            .hide()
        )
        timestamp_df = trace_df[
            [
                "activity",
                "time:timestamp",
                "time:end_timestamp",
                "timestamp_correctness",
                "correctness_confidence",
            ]
        ]
        timestamp_df = u.Conversion.rename_columns(timestamp_df)
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
                "traces_count": Trace.manager.filter(
                    patient_journey__name=patient_journey_name
                ).count(),
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
        activity_relevance = row["Activity Relevance"]
        if activity_relevance == "Moderate Relevance":
            return ["background-color: orange"] * len(row)

        if activity_relevance == "Low Relevance":
            return ["background-color: red"] * len(row)

        return [""] * len(row)

    @staticmethod
    def color_timestamp_correctness(row):
        """Color a specific cell based on the timestamp correctness confidence."""
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
            config={"displaylogo": False, "displayModeBar": False, "showTips": False},
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
            config={
                "displaylogo": False,
                "displayModeBar": False,
                "staticPlot": True,
                "showTips": False,
            },
        )


class EvaluationView(FormView):
    """View for displaying all extracted traces and DFG image with filter selection."""

    form_class = EvaluationForm
    template_name = "evaluation.html"
    success_url = reverse_lazy("evaluation")

    def get_context_data(self, **kwargs):
        """Prepare the data for the evaluation page."""
        context = super().get_context_data(**kwargs)

        self.initiate_evaluation_configuration()
        configuration = self.request.session.get("filter_settings")
        activity_key = configuration.get("activity_key")

        # Query the database to get all traces
        query_dict = self.request.session.get("query_dict")
        if query_dict is not None:
            query = self.create_query(query_dict)
            event_log_df = u.DataFrameUtilities.get_events_df(query)
            traces = Trace.manager.filter(query)
        else:
            event_log_df = u.DataFrameUtilities.get_events_df()
            traces = Trace.manager.all()

        cohorts = Cohort.manager.filter(trace__in=traces)
        print(
            cohorts.values(
                "trace", "age", "sex", "origin", "condition", "preexisting_condition"
            )
        )
        cohorts_data = list(
            cohorts.values(
                "trace", "age", "sex", "origin", "condition", "preexisting_condition"
            )
        )

        cohorts_df = pd.DataFrame(cohorts_data)
        cohorts_df["age"] = cohorts_df["age"].astype(pd.Int64Dtype())
        filter_dict = {
            "event_type": configuration.get("event_types"),
            "attribute_location": configuration.get("locations"),
        }
        if not event_log_df.empty:
            event_log_df = u.DataFrameUtilities.filter_dataframe(
                event_log_df, filter_dict
            )

            # Drop unwanted columns
            event_log_df = event_log_df.drop(
                columns=[
                    "activity_relevance",
                    "timestamp_correctness",
                    "correctness_confidence",
                ]
            )

            context.update(
                {
                    "all_dfg_img": u.Conversion.create_dfg_from_df(
                        event_log_df, activity_key
                    ),
                    "event_log_table": u.Conversion.create_html_table_from_df(
                        event_log_df
                    ),
                    "cohorts_table": u.Conversion.create_html_table_from_df(cohorts_df),
                }
            )

        context.update({"form": EvaluationForm(initial=configuration)})

        self.request.session["event_log"] = event_log_df.to_json()

        return context

    @staticmethod
    def create_query(query_dict):
        """Create a query object based on the given dictionary."""
        query = Q(
            cohort__age__gte=query_dict.get("min_age"),
            cohort__age__lte=query_dict.get("max_age"),
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

    def initiate_evaluation_configuration(self):
        """Initialize form with default values if no filter settings are present."""

        configuration = self.request.session.get("filter_settings")
        if configuration is None:
            configuration = {
                "event_types": [event_type[0] for event_type in EVENT_TYPES],
                "locations": [location[0] for location in LOCATIONS],
                "activity_key": ACTIVITY_KEYS[0][0],
            }

        self.request.session["filter_settings"] = configuration


class DownloadXesEvaluationView(DownloadXesView):
    """Download one or more XES files based on the types specified in POST request,
    bundled into a ZIP file if multiple."""

    @staticmethod
    def process_trace_type(request, trace_type):
        """Process and provide the XES files to be downloaded based on the trace type."""
        configuration = request.session.get("filter_settings")
        activity_key = configuration.get("activity_key")

        if trace_type == "event_log":
            # Process event log data into XES format
            df = pd.read_json(request.session.get("event_log"))

            if df.empty:
                return None

            event_log_xes = u.Conversion.dataframe_to_xes(
                df, name="event_log", activity_key=activity_key
            )
            return event_log_xes

        return None
