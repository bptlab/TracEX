"""This file contains the views for the extraction app.
Some unused imports have to be made because of architectural requirement."""
# pylint: disable=unused-argument
import os
import pm4py
import pandas as pd
from django.db.models import Q

from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse

from tracex.logic import utils
from tracex.logic.constants import IS_TEST
from .forms import JourneyForm, ResultForm, FilterForm
from .logic.orchestrator import Orchestrator, ExtractionConfiguration
from .models import Trace, PatientJourney

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
        if IS_TEST:
            default_journey = PatientJourney.manager.get(name="default_journey_name")
            configuration = ExtractionConfiguration(
                patient_journey=default_journey.patient_journey,
            )
        else:
            uploaded_file = self.request.FILES.get("file")
            content = uploaded_file.read().decode("utf-8")
            form.instance.patient_journey = content

            configuration = ExtractionConfiguration(
                patient_journey=content,
            )
        orchestrator = Orchestrator(configuration)
        response = super().form_valid(form)
        orchestrator.db_objects["patient_journey"] = self.object.id

        return response


class JourneyFilterView(generic.FormView):
    """View for selecting extraction results filter"""

    form_class = FilterForm
    template_name = "filter_journey.html"
    success_url = reverse_lazy("result")

    def form_valid(self, form):
        """Run extraction pipeline and save the filter settings in the cache."""
        orchestrator = Orchestrator.get_instance()
        orchestrator.configuration.update(
            event_types=form.cleaned_data["event_types"],
            locations=form.cleaned_data["locations"],
        )
        if IS_TEST:
            default_journey = PatientJourney.manager.get(name="default_journey_name")
            trace = (
                Trace.manager.filter(patient_journey=default_journey)
                .order_by("last_modified")
                .first()
            )
            print(trace)
            event_objects = trace.events.all()
            data = {
                "case_id": trace.id,
                "activity": [event.activity for event in event_objects],
                "event_type": [event.event_type for event in event_objects],
                "start": [event.start for event in event_objects],
                "end": [event.end for event in event_objects],
                "duration": [event.duration for event in event_objects],
                "attribute_location": [event.location for event in event_objects],
            }
            orchestrator.data = pd.DataFrame(data)
            orchestrator.simulate_extraction(view=self)
        else:
            orchestrator.run(view=self)

        utils.Conversion.create_xes_from_df(
            orchestrator.data,
            name="single_trace",
            key=orchestrator.configuration.activity_key,
        )
        self.request.session["is_extracted"] = True
        self.request.session.save()

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
        event_types = self.flatten_list(orchestrator.configuration.event_types)
        filter_dict = {
            "concept:name": event_types,
            "attribute_location": orchestrator.configuration.locations,
        }

        output_path_xes = f"{str(utils.output_path / 'single_trace')}_event_type.xes"
        single_trace_df = pm4py.read_xes(output_path_xes)

        # 2. Sort and filter the single journey dataframe
        single_trace_df = self.sort_dataframe(single_trace_df)
        single_trace_df_filtered = self.filter_dataframe(single_trace_df, filter_dict)
        # 3. Append the single journey dataframe to the all traces dataframe

        # TODO: remove comment once cohort is implemented
        # condition = Cohort.manager.get(pk=orchestrator.db_objects["cohort"]).condition
        # query = Q(cohort__condition=condition)
        all_traces_df = self.get_events_df()
        if not all_traces_df.empty:
            all_traces_df = utils.Conversion.prepare_df_for_xes_conversion(
                all_traces_df, orchestrator.configuration.activity_key
            )
            utils.Conversion.align_df_datatypes(single_trace_df_filtered, all_traces_df)
            all_traces_df = pd.concat(
                [all_traces_df, single_trace_df_filtered],
                ignore_index=True,
                axis="rows",
            )
            all_traces_df.groupby(
                "case:concept:name", group_keys=False, sort=False
            ).apply(self.sort_dataframe)
            all_traces_df_filtered = self.filter_dataframe(all_traces_df, filter_dict)
        else:
            all_traces_df_filtered = single_trace_df_filtered

        # 4. Save all information in context to display on website
        context["form"] = ResultForm(
            initial={
                "event_types": orchestrator.configuration.event_types,
                "locations": orchestrator.configuration.locations,
            }
        )
        context["journey"] = orchestrator.configuration.patient_journey
        context["dfg_img"] = utils.Conversion.create_dfg_from_df(
            single_trace_df_filtered
        )
        context["xes_html"] = utils.Conversion.create_html_from_xes(
            single_trace_df_filtered
        ).getvalue()
        context["all_dfg_img"] = utils.Conversion.create_dfg_from_df(
            all_traces_df_filtered
        )
        context["all_xes_html"] = utils.Conversion.create_html_from_xes(
            all_traces_df_filtered
        ).getvalue()

        return context

    def form_valid(self, form):
        """Save the filter settings in the cache."""
        orchestrator = Orchestrator.get_instance()
        orchestrator.configuration.update(
            # This should not be necessary, unspecified values should be unchanged
            patient_journey=orchestrator.configuration.patient_journey,
            event_types=form.cleaned_data["event_types"],
            locations=form.cleaned_data["locations"],
        )
        return super().form_valid(form)

    @staticmethod
    def get_events_df(query: Q = None):
        """Get all events from the database, or filter them by a query and return them as a dataframe."""
        traces = Trace.manager.all() if query is None else Trace.manager.filter(query)
        event_data = []

        for trace in traces:
            events = trace.events.all()
            for event in events:
                event_data.append(
                    {
                        "case_id": trace.id,
                        "activity": event.activity,
                        "event_type": event.event_type,
                        "start": event.start,
                        "end": event.end,
                        "duration": event.duration,
                        "attribute_location": event.location,
                    }
                )
        events_df = pd.DataFrame(event_data)

        return events_df

    @staticmethod
    def flatten_list(original_list):
        """Flatten a list of lists."""
        flattened_list = []
        for item in original_list:
            if "," in item:
                flattened_list.extend(item.split(", "))
            else:
                flattened_list.append(item)
        return flattened_list

    @staticmethod
    def sort_dataframe(df):
        """Sort a dataframe containing a trace by timestamp."""
        sorted_df = df.sort_values(by="start_timestamp", inplace=False)
        return sorted_df

    @staticmethod
    def filter_dataframe(df, filter_dict):
        """Filter a dataframe."""
        filter_conditions = [
            df[column].isin(values) for column, values in filter_dict.items()
        ]
        combined_condition = pd.Series(True, index=df.index)

        for condition in filter_conditions:
            combined_condition &= condition

        return df[combined_condition]


class SaveSuccessView(generic.TemplateView):
    """View for displaying the save success page."""

    template_name = "save_success.html"

    def get_context_data(self, **kwargs):
        """Prepare the data for the save success page."""
        context = super().get_context_data(**kwargs)
        orchestrator = Orchestrator.get_instance()
        orchestrator.save_results_to_db()

        return context
