from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("/journey/", views.JourneyInputView, name="journey"),
    # path("/journey/wait/", views.WaitingView, name="waitingroom"),
    # path("/journey/log/", views.EventLogView, name="eventlog"),
    # path("/journey/dfg/", views.DfgView, name="dfg")
]
