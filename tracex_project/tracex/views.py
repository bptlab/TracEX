"""This file contains the views for the landing page of the tracex app."""
from django.shortcuts import render

def landing_page(request):
    """Renders the landing page."""
    return render(request, "landing_page.html")
