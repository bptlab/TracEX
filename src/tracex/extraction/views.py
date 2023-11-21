import csv
from io import StringIO

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic

from .forms import JourneyForm


def index(request):
    return HttpResponse("Hello, world. You're at the index.")


class JourneyInputView(generic.FormView):
    form_class = JourneyForm
    template_name = "upload_journey.html"
    success_url = reverse_lazy("result")

    # def form_valid(self, form):
    #     eventlog = self.process_and_save_file(form.cleaned_data["file"])
    #     self.success_url += f"?eventlog={eventlog}"
    #
    #     return super().form_valid(form)
    #
    # def process_and_save_file(self, file):
    #     # Placeholder function for processing and saving the file
    #
    #     return f"Processed data from file: {file.name}"


class ResultView(generic.TemplateView):
    template_name = "result_eventlog.html"

    def get_context_data(self, **kwargs):
        eventlog = self.request.GET.get("eventlog", "")
        context = super().get_context_data(**kwargs)
        context["csv_data"] = self.parse_csv(eventlog)
        return context

    def parse_csv(self, csv_data):
        # Parse CSV data and return as a list of dictionaries
        data = []
        if csv_data:
            csv_reader = csv.DictReader(StringIO(csv_data))
            for row in csv_reader:
                data.append(row)
        return data
