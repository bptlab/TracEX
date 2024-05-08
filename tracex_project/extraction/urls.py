"""tracex URL Configuration for extraction app"""
from django.urls import path

from . import views

urlpatterns = [
    path("download-xes/", views.DownloadXesView.as_view(), name="download_xes"),
    path(
        "extraction/",
        views.JourneyInputSelectView.as_view(),
        name="choose_input_method",
    ),
    path(
        "extraction/upload/", views.JourneyUploadView.as_view(), name="journey_upload"
    ),
    path(
        "extraction/select/", views.JourneySelectView.as_view(), name="journey_select"
    ),
    path(
        "extraction/select/<int:pk>/",
        views.JourneyDetailView.as_view(),
        name="journey_details",
    ),
    path("extraction/result/", views.ResultView.as_view(), name="result"),
    path(
        "extraction/filter/", views.JourneyFilterView.as_view(), name="journey_filter"
    ),
    path("extraction/saved/", views.SaveSuccessView.as_view(), name="save_success"),
    path("evaluation/", views.EvaluationView.as_view(), name="evaluation"),
]
