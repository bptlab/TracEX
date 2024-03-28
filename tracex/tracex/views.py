"""This file contains the views for the landing page of the tracex app."""
from django.shortcuts import render
import django.views.generic as generic


class TracexLandingPage(generic.TemplateView):
    """View for the landing page of the tracex app."""
    
    template_name = "landing_page.html"

    def get_context_data(self, **kwargs):
        """Reset session variables."""
        context = super().get_context_data(**kwargs)
        self.request.session.flush()
        return context