"""tracex URL Configuration for tracex app"""
from django.urls import path
from patient_journey_generator import views


urlpatterns = [
    path(
        "patient_journey_generator/",
        views.JourneyGeneratorOverviewView.as_view(),
        name="journey_generator_overview",
    ),
    path(
        "patient_journey_generator/generation/",
        views.JourneyGenerationView.as_view(),
        name="journey_generation",
    ),
]
