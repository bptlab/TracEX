"""This file contains the views for the extraction app.
Some unused imports have to be made because of architectual requirement."""
# pylint: disable=unused-argument
import os
import tempfile
import base64
from io import StringIO, BytesIO

import pm4py
import pandas

from django.urls import reverse_lazy
from django.views import generic
from django.core.cache import cache
from django.shortcuts import redirect

# necessary due to Windows error. see information for your os here:
# https://stackoverflow.com/questions/35064304/runtimeerror-make-sure-the-graphviz-executables-are-on-your-systems-path-aft
os.environ["PATH"] += os.pathsep + "C:/Program Files/Graphviz/bin/"

from .forms import JourneyForm, GenerationForm, ResultForm
from .prototype import (
    input_handling,
    input_inquiry,
    create_all_trace_xes,
    utils,
    output_handling,
)

# set IS_TEST = False if you want to run the pipeline
IS_TEST = False


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
        cache.set("journey", form.cleaned_data["journey"].read().decode("utf-8"))
        cache.set("event_types", form.cleaned_data["event_types"])
        cache.set("locations", form.cleaned_data["locations"])
        cache.set("is_extracted", False)
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

        if IS_TEST:
            with open(str(utils.input_path / "journey_synth_covid_1.txt"), "r") as file:
                journey = file.read()
        else:
            journey = input_inquiry.create_patient_journey()

        cache.set("journey", journey)
        context["generated_journey"] = journey
        return context

    def form_valid(self, form):
        """Save the generated journey in the cache."""
        cache.set("event_types", form.cleaned_data["event_types"])
        cache.set("locations", form.cleaned_data["locations"])
        cache.set("is_extracted", False)
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
        journey = cache.get("journey")
        event_types = self.flatten_list(cache.get("event_types"))
        locations = cache.get("locations")
        filter_dict = {"concept:name": event_types, "attribute_location": locations}

        if cache.get("is_extracted") is None:
            is_extracted = True
        else:
            is_extracted = cache.get(
                "is_extracted"
            )  # false if coming from input or generation

        # read single journey into dataframe
        single_trace_df = pm4py.read_xes(
            self.get_xes_output_path(
                journey, is_test=IS_TEST, is_extracted=is_extracted
            )
        )

        # prepare single journey xes
        single_trace_df = self.sort_trace(single_trace_df)
        output_df_filtered = self.filter_dataframe(single_trace_df, filter_dict)

        # prepare all journey xes
        all_traces_df = pm4py.read_xes(
            self.get_all_xes_output_path(is_test=IS_TEST, is_extracted=is_extracted)
        )
        all_traces_df = all_traces_df.groupby(
            "case:concept:name", group_keys=False, sort=False
        ).apply(self.sort_trace)
        all_traces_df_filtered = self.filter_dataframe(all_traces_df, filter_dict)

        context["form"] = ResultForm(
            initial={"event_types": cache.get("event_types"), "locations": locations}
        )
        context["journey"] = journey
        context["dfg_img"] = self.create_dfg_png_from_df(output_df_filtered)
        context["xes_html"] = self.create_html_from_xes(output_df_filtered).getvalue()
        context["all_dfg_img"] = self.create_dfg_png_from_df(all_traces_df_filtered)
        context["all_xes_html"] = self.create_html_from_xes(
            all_traces_df_filtered
        ).getvalue()

        is_extracted = True
        cache.set("is_extracted", is_extracted)
        return context

    def form_valid(self, form):
        """Save the filter settings in the cache."""
        cache.set("event_types", form.cleaned_data["event_types"])
        cache.set("locations", form.cleaned_data["locations"])
        return super().form_valid(form)

    def get_xes_output_path(self, journey, is_test=False, is_extracted=False):
        """Create the xes file for the single journey."""
        if not is_test or is_extracted:
            output_path_csv = input_handling.convert_text_to_csv(journey)
            output_path_xes = create_all_trace_xes.create_all_trace_xes(
                output_path_csv, key="event_type", suffix="_1"
            )
        else:
            output_path_xes = str(utils.output_path / "all_traces_event_type_1.xes")
        return output_path_xes

    def get_all_xes_output_path(
        self, is_test=False, is_extracted=False, key="event_type", suffix=""
    ):
        """Create the xes file for all journeys."""
        if not is_test or is_extracted:
            output_handling.append_csv()
            all_traces_xes_path = create_all_trace_xes.create_all_trace_xes(
                utils.CSV_ALL_TRACES, key=key, suffix=suffix
            )
        else:
            all_traces_xes_path = (
                str(utils.output_path / "all_traces_") + key + suffix + ".xes"
            )
        return all_traces_xes_path

    def create_html_from_xes(self, df):
        """Create html table from xes file."""
        xes_html_buffer = StringIO()
        pandas.DataFrame.to_html(df, buf=xes_html_buffer)
        return xes_html_buffer

    def create_dfg_png_from_df(self, df):
        """Create png image from xes file."""
        dfg_img_buffer = BytesIO()
        output_dfg_file = pm4py.discover_dfg(
            df, "concept:name", "time:timestamp", "case:concept:name"
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file_path = temp_file.name
            pm4py.save_vis_dfg(
                output_dfg_file[0],
                output_dfg_file[1],
                output_dfg_file[2],
                temp_file_path,
                rankdir="TB",
            )
        with open(temp_file_path, "rb") as temp_file:
            dfg_img_buffer.write(temp_file.read())
        os.remove(temp_file_path)
        dfg_img_base64 = base64.b64encode(dfg_img_buffer.getvalue()).decode("utf-8")
        return dfg_img_base64

    def flatten_list(self, original_list):
        """Flatten a list of lists."""
        flattened_list = []
        for item in original_list:
            if "," in item:
                flattened_list.extend(item.split(", "))
            else:
                flattened_list.append(item)

        return flattened_list

    def sort_trace(self, df):
        """Sort a trace by timestamp."""
        sorted_df = df.sort_values(by="time:timestamp", inplace=False)
        return sorted_df

    def filter_dataframe(self, df, filter_dict):
        """Filter a dataframe."""
        filter_conditions = [
            df[column].isin(values) for column, values in filter_dict.items()
        ]
        combined_condition = pandas.Series(True, index=df.index)

        for condition in filter_conditions:
            combined_condition &= condition

        return df[combined_condition]
