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
    success_url = reverse_lazy("result")

    def form_valid(self, form):
        file_content = form.cleaned_data["journey"].read().decode("utf-8")
        output = input_handling.convert_text_to_bulletpoints(file_content)
        cache.set("eventlog", output)
        return super().form_valid(form)


class ResultView(generic.TemplateView):
    template_name = "result_eventlog.html"

    def get_context_data(self, **kwargs):
        eventlog = self.request.GET.get("eventlog", "")
        context = super().get_context_data(**kwargs)
        context["eventlog"] = cache.get("eventlog")
        return context
