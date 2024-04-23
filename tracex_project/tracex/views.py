"""This file contains the views for the landing page of the tracex app."""
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from .forms import ApiKeyForm
import os


class TracexLandingPage(TemplateView):
    """View for the landing page of the tracex app."""

    template_name = "landing_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request.session.flush()
        api_key = os.getenv('OPENAI_API_KEY')
        print("API Key:", api_key)
        context['prompt_for_key'] = not bool(api_key)
        context['form'] = ApiKeyForm()
        return context


def set_api_key(request):
    if request.method == 'POST':
        form = ApiKeyForm(request.POST)
        if form.is_valid():
            api_key = form.cleaned_data['api_key']
            os.environ['OPENAI_API_KEY'] = api_key

            return redirect('landing_page')
        else:

            return render(request, 'landing_page', {'form': form})
    else:
        form = ApiKeyForm()
    return render(request, 'landing_page', {'form': form})
