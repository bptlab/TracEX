from django.http import HttpResponse
from django.views import generic

from forms import JourneyForm


def index(request):
    return HttpResponse("Hello, world. You're at the index.")


class JourneyInputView(generic.FormView):
    form_class = JourneyForm
