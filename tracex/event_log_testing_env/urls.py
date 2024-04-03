"""tracex URL Configuration for event log testing environment app"""
from django.urls import path
from . import views


urlpatterns = [
    path(
        "testing_environment/",
        views.EventLogTestingOverviewView.as_view(),
        name="testing_environment",
    ),
    # path(
    #     "event_log_testing_environment/result/",
    #     views.JourneyGenerationView.as_view(),
    #     name="journey_generation",
    # ),
]
