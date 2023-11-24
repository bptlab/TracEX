from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("journey/", views.JourneyInputView.as_view(), name="journey"),
    path("journey/result/", views.ResultView.as_view(), name="result"),
    path("journey/processing", views.ProcessingView.as_view(), name="processing"),
]
