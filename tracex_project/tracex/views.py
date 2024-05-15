"""This file contains the views for the landing page of the tracex app."""
import os
from django.views.generic import TemplateView, RedirectView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from tracex.forms import ApiKeyForm

class TracexLandingPage(TemplateView):
    """View for the landing page of the tracex app."""
    template_name = "landing_page.html"

    def get(self, _request, *_args, **kwargs):
        """Handles GET requests by initializing a form for API key entry and adding it to the context."""
        form = ApiKeyForm()
        context = self.get_context_data(**kwargs)
        context['form'] = form

        return self.render_to_response(context)

    def post(self, request):
        """Handles POST requests by processing a submitted form containing an API key.
        If valid, saves the API key to the environment and redirects to the landing page;
        otherwise, renders the form with errors."""
        form = ApiKeyForm(request.POST)
        if form.is_valid():
            api_key = form.cleaned_data['api_key']
            os.environ['OPENAI_API_KEY'] = api_key  # This sets it for the current process only
            return redirect('landing_page')

        return render(request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        """Retrieves and returns the base context data enhanced with the presence check for the API key.
        Indicates if a prompt for the API key is needed based on its absence."""
        context = super().get_context_data(**kwargs)
        self.request.session.flush()
        api_key = os.getenv('OPENAI_API_KEY')
        context['prompt_for_key'] = not bool(api_key)

        return context

class ResetApiKey(RedirectView):
    """View for the resetting the API key."""

    url = reverse_lazy("landing_page")

    def get(self, request, *args, **kwargs):
        """Handles GET requests by deleting the API key from the environment and redirecting to the landing page."""
        del os.environ['OPENAI_API_KEY']

        return super().get(request, *args, **kwargs)
