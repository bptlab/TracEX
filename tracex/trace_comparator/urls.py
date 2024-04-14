"""tracex URL Configuration for event log testing environment app"""
from django.urls import path
from . import views


urlpatterns = [
    path(
        "testing_environment/",
        views.EventLogTestingOverviewView.as_view(),
        name="testing_environment",
    ),
    path(
        "testing_environment/comparison/",
        views.EventLogTestingComparisonView.as_view(),
        name="testing_comparison",
    ),
    path(
        "testing_environment/result/",
        views.EventLogTestingResultView.as_view(),
        name="testing_result",
    ),
]
