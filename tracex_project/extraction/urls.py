"""tracex URL Configuration for extraction app"""
from django.urls import path

from . import views

urlpatterns = [
    path('download-xes/', views.download_xes, name='download_xes'),
    path("extraction/", views.JourneyInputView.as_view(), name="journey_input"),
    path("extraction/result/", views.ResultView.as_view(), name="result"),
    path(
        "extraction/filter/", views.JourneyFilterView.as_view(), name="journey_filter"
    ),
    path("extraction/saved/", views.SaveSuccessView.as_view(), name="save_success"),
]
