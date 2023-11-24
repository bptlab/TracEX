import pm4py
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.core.cache import cache
import sys

from .forms import JourneyForm
from .prototype import input_handling


def index(request):
    return HttpResponse("Hello, world. You're at the index.")


class JourneyInputView(generic.FormView):
    form_class = JourneyForm
    template_name = "upload_journey.html"
    success_url = reverse_lazy("processing")

    def form_valid(self, form):
        cache.set("journey", form.cleaned_data["journey"])
        cache.set("event_types", form.cleaned_data["event_types"])
        cache.set("locations", form.cleaned_data["locations"])
        return super().form_valid(form)


class ProcessingView(generic.TemplateView):
    template_name = "processing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        journey = cache.get("journey").read().decode("utf-8")
        event_types = cache.get("event_types")
        output_path = input_handling.convert_inp_to_xes(journey)
        with open(output_path) as f:
            output = f.read()

        # attempt to render dfg
        # output = pm4py.read_xes(output_path)
        # output_dfg_file = pm4py.discover_dfg(output, 'concept:Activity', 'date:StartDate', 'caseID')
        # output_dfg = pm4py.view_dfg(output_dfg_file[0], output_dfg_file[1], output_dfg_file[2])

        context["journey"] = journey
        context["event_types"] = event_types
        context["output"] = output
        return context


class ResultView(generic.TemplateView):
    template_name = "result_eventlog.html"

    def get_context_data(self, **kwargs):
        eventlog = self.request.GET.get("event_log", "")
        context = super().get_context_data(**kwargs)
        context["eventlog"] = cache.get("eventlog")
        return context
