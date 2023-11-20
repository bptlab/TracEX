from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("/journey/", views.JourneyInputView, name="journey"),
    path("/journey/result_<str:eventlog>/", views.EventLogView, name="eventlog"),
    # path("/journey/result_<str:eventlog>/dfg/", views.DfgView, name="dfg")
]
