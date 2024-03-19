"""tracex URL Configuration for extraction app"""
from django.urls import path

from . import views

urlpatterns = [
    path(
        "", views.redirect_to_selection, name="redirect_to_selection"
    ),  # Add a new view for redirection
    path("selection/", views.SelectionView.as_view(), name="selection"),
    path(
        "generation/", views.JourneyGenerationView.as_view(), name="journey_generation"
    ),
    path("journey/", views.JourneyInputView.as_view(), name="journey_input"),
    path("journey/result/", views.ResultView.as_view(), name="result"),
    path("journey/processing/", views.ProcessingView.as_view(), name="processing"),
    path("journey/saved/", views.SaveSuccessView.as_view(), name="save_success"),
]
