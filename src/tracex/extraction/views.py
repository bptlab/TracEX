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

# necessary due to Windows error. see information for your os here:
# https://stackoverflow.com/questions/35064304/runtimeerror-make-sure-the-graphviz-executables-are-on-your-systems-path-aft
os.environ["PATH"] += os.pathsep + "C:/Program Files/Graphviz/bin/"

from .forms import JourneyForm
from .prototype import input_handling


def index(request):
    return HttpResponse("Hello, world. You're at the index.")


class JourneyInputView(generic.FormView):
    form_class = JourneyForm
    template_name = "upload_journey.html"
    success_url = reverse_lazy("result")

    def form_valid(self, form):
        cache.set("journey", form.cleaned_data["journey"])
        cache.set("event_types", form.cleaned_data["event_types"])
        cache.set("locations", form.cleaned_data["locations"])
        return super().form_valid(form)


class ProcessingView(generic.TemplateView):
    template_name = "processing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class ResultView(generic.TemplateView):
    template_name = "result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        journey = cache.get("journey").read().decode("utf-8")
        event_types = cache.get("event_types")
        locations = cache.get("locations")
        output_path = input_handling.convert_inp_to_xes(journey)

        # convert xes dataframe to html and write to buffer
        output_df = pm4py.read_xes(output_path)
        xes_html_buffer = StringIO()
        pandas.DataFrame.to_html(output_df, buf=xes_html_buffer)

        # render dfg from xes dataframe
        dfg_img_buffer = BytesIO()
        output_dfg_file = pm4py.discover_dfg(
            output_df, "concept:Activity", "date:StartDate", "caseID"
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

        context["event_types"] = event_types
        context["locations"] = locations
        context["journey"] = journey
        context["dfg_img"] = dfg_img_base64
        context["xes_html"] = xes_html_buffer.getvalue()
        return context
