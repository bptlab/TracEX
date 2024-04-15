"""tracex URL Configuration for trace testing environment app"""
from django.urls import path
from . import views


urlpatterns = [
    path(
        "testing_environment/",
        views.TraceTestingOverviewView.as_view(),
        name="testing_environment",
    ),
    path(
        "testing_environment/comparison/",
        views.TraceTestingComparisonView.as_view(),
        name="testing_comparison",
    ),
    path(
        "testing_environment/result/",
        views.TraceTestingResultView.as_view(),
        name="testing_result",
    ),
]
