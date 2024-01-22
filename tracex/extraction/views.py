"""This file contains the views for the extraction app.
Some unused imports have to be made because of architectural requirement."""
# pylint: disable=unused-argument
import os

import pm4py
import pandas as pd

from django.urls import reverse_lazy
from django.views import generic
from django.core.cache import cache
from django.shortcuts import redirect

from .forms import JourneyForm, GenerationForm, ResultForm
from .prototype import (input_handling, input_inquiry, create_xes, output_handling, )
from .logic.orchestrator import Orchestrator, ExtractionConfiguration
from .logic import utils

# necessary due to Windows error. see information for your os here:
# https://stackoverflow.com/questions/35064304/runtimeerror-make-sure-the-graphviz-executables-are-on-your-systems-path-aft
os.environ["PATH"] += os.pathsep + "C:/Program Files/Graphviz/bin/"

IS_TEST = False  # Controls the presentation mode of the pipeline, set to False if you want to run the pipeline


def redirect_to_selection(request):
    """Redirect to selection page."""
    return redirect("selection")


class JourneyInputView(generic.FormView):
    """View for uploading a patient journey."""

    form_class = JourneyForm
    template_name = "upload_journey.html"
    success_url = reverse_lazy("processing")

    def form_valid(self, form):
        """Save the uploaded journey in the cache."""
        cache.set("is_extracted", False)
        orchestrator = Orchestrator.get_instance()
        orchestrator.configuration.update(
            event_types=form.cleaned_data["event_types"],
            locations=form.cleaned_data["locations"],
            patient_journey=form.cleaned_data["journey"].read().decode("utf-8"),
        )
        return super().form_valid(form)


class SelectionView(generic.TemplateView):
    """View for selecting a patient journey."""

    template_name = "selection.html"


class JourneyGenerationView(generic.FormView):
    """View for generating a patient journey."""

    form_class = GenerationForm
    template_name = "generation.html"
    success_url = reverse_lazy("processing")

    def get_context_data(self, **kwargs):
        """Generate a patient journey and save it in the cache."""
        context = super().get_context_data(**kwargs)

        orchestrator = Orchestrator.get_instance()

        if IS_TEST:
            with open(str(utils.input_path / "journey_synth_covid_1.txt"), "r") as file:
                journey = file.read()
        else:
            orchestrator.generate_patient_journey()
            journey = orchestrator.configuration.patient_journey

        orchestrator.configuration.update(patient_journey=journey)  # In case of test mode off, this is already executed from generate_patient_journey()
        context["generated_journey"] = orchestrator.configuration.patient_journey
        return context

    def form_valid(self, form):
        """Save the generated journey in the cache."""
        cache.set("is_extracted", False)
        orchestrator = Orchestrator.get_instance()
        orchestrator.configuration.update(
                event_types=form.cleaned_data["event_types"],
                locations=form.cleaned_data["locations"],
        )
        return super().form_valid(form)


class ProcessingView(generic.TemplateView):
    """View for processing the patient journey."""

    template_name = "processing.html"

    def get(self, request, *args, **kwargs):
        """Redirect to result page."""
        return redirect("result")


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
        filter_dict = {"concept:name": event_types, "attribute_location": orchestrator.configuration.locations}
        is_extracted = True if cache.get("is_extracted") is None else cache.get("is_extracted")

        # 1. Run the pipeline to create the single journey dataframe from csv
        if not (IS_TEST or is_extracted):
            output_path_csv = orchestrator.run()
            output_path_xes = utils.Conversion.create_xes(
                output_path_csv, name="single_trace", key=orchestrator.configuration.activity_key
            )
        else:
            output_path_xes = (
                    str(utils.output_path / "single_trace") + "_" + orchestrator.configuration.activity_key + ".xes"
            )
        single_trace_df = pm4py.read_xes(output_path_xes)

        # 2. Sort and filter the single journey dataframe
        single_trace_df = self.sort_dataframe(single_trace_df)
        output_df_filtered = self.filter_dataframe(single_trace_df, filter_dict)

        # 3. Append the single journey dataframe to the all traces dataframe
        all_traces_df = pm4py.read_xes(
            utils.get_all_xes_output_path(is_test=IS_TEST, is_extracted=is_extracted)
        )
        all_traces_df = all_traces_df.groupby(
            "case:concept:name", group_keys=False, sort=False
        ).apply(self.sort_dataframe)
        all_traces_df_filtered = self.filter_dataframe(all_traces_df, filter_dict)

        # 4. Save all information in context to display on website
        context["form"] = ResultForm(
            initial={
                "event_types": orchestrator.configuration.event_types,
                "locations": orchestrator.configuration.locations,
            }
        )
        context["journey"] = orchestrator.configuration.patient_journey
        context["dfg_img"] = utils.Conversion.create_dfg_png_from_df(output_df_filtered)
        context["xes_html"] = utils.Conversion.create_html_from_xes(output_df_filtered).getvalue()
        context["all_dfg_img"] = utils.Conversion.create_dfg_png_from_df(all_traces_df_filtered)
        context["all_xes_html"] = utils.Conversion.create_html_from_xes(
            all_traces_df_filtered
        ).getvalue()
        cache.set("is_extracted", True)

        return context

    def form_valid(self, form):
        """Save the filter settings in the cache."""
        orchestrator = Orchestrator.get_instance()
        configuration = {
            "event_types": form.cleaned_data["event_types"],
            "locations": form.cleaned_data["locations"],
        }
        orchestrator.configuration.update(**configuration)
        return super().form_valid(form)

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
        sorted_df = df.sort_values(by="time:timestamp", inplace=False)
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
