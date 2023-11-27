import pm4py
import pandas
import os
import tempfile
import base64

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.core.cache import cache
from io import StringIO, BytesIO
from django.shortcuts import redirect

# necessary due to Windows error. see information for your os here:
# https://stackoverflow.com/questions/35064304/runtimeerror-make-sure-the-graphviz-executables-are-on-your-systems-path-aft
os.environ["PATH"] += os.pathsep + "C:/Program Files/Graphviz/bin/"

from .forms import JourneyForm, GenerationForm
from .prototype import input_handling, input_inquiry


def redirect_to_selection(request):
    return redirect("selection")


class JourneyInputView(generic.FormView):
    form_class = JourneyForm
    template_name = "upload_journey.html"
    success_url = reverse_lazy("processing")

    def form_valid(self, form):
        cache.set("journey", form.cleaned_data["journey"].read().decode("utf-8"))
        cache.set("event_types", form.cleaned_data["event_types"])
        cache.set("locations", form.cleaned_data["locations"])
        return super().form_valid(form)


class SelectionView(generic.TemplateView):
    template_name = "selection.html"


class JourneyGenerationView(generic.FormView):
    form_class = GenerationForm
    template_name = "generation.html"
    success_url = reverse_lazy("processing")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_journey = input_inquiry.create_patient_journey()
        cache.set("journey", patient_journey)
        context["generated_journey"] = patient_journey
        return context

    def form_valid(self, form):
        cache.set("event_types", form.cleaned_data["event_types"])
        cache.set("locations", form.cleaned_data["locations"])
        return super().form_valid(form)


class ProcessingView(generic.TemplateView):
    template_name = "processing.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return redirect("result")


class ResultView(generic.TemplateView):
    template_name = "result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        journey = cache.get("journey")
        event_types = cache.get("event_types")
        locations = cache.get("locations")
        output_path = input_handling.convert_inp_to_xes(journey)
        output_df = pm4py.read_xes(output_path)
        context["event_types"] = event_types
        context["locations"] = locations
        context["journey"] = journey
        context["dfg_img"] = self.create_dfg_png_from_df(output_df)
        context["xes_html"] = self.create_html_from_xes(output_df).getvalue()
        return context

    def create_html_from_xes(self, df):
        xes_html_buffer = StringIO()
        pandas.DataFrame.to_html(df, buf=xes_html_buffer)
        return xes_html_buffer

    def create_dfg_png_from_df(self, df):
        dfg_img_buffer = BytesIO()
        output_dfg_file = pm4py.discover_dfg(
            df, "concept:Activity", "date:StartDate", "caseID"
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
