"""tracex URL Configuration for database result app"""
from django.urls import path
from . import views


urlpatterns = [
    path(
        "db_results/",
        views.DbResultsOverviewView.as_view(),
        name="db_results_overview",
    ),
    path(
        "db_results/metrics_overview/",
        views.MetricsOverviewView.as_view(),
        name="metrics_overview",
    ),
    path(
        "db_results/metrics_dashboard/",
        views.MetricsDashboardView.as_view(),
        name="metrics_dashboard",
    ),
]
