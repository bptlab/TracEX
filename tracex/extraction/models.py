"""This module contains the models for the extraction app."""
from django.db import models

from .logic.constants import EVENT_TYPES, LOCATIONS


class PatientJourney(models.Model):
    """Model for the patient journey input."""

    name = models.CharField(
        max_length=100,
        help_text="If no name is provided, the name of the uploaded file will be used.",
        verbose_name="Name for your patient journey",
        unique=False,
    )
    patient_journey = models.TextField(unique=True)


class Trace(models.Model):
    """Model for a single trace, extracted from a patient journey."""

    patient_journey = models.ForeignKey(
        PatientJourney, on_delete=models.CASCADE, related_name="trace"
    )
    event_information = models.TextField()
    event_type = models.CharField(max_length=25, choices=EVENT_TYPES)
    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.DurationField()
    location = models.CharField(max_length=25, choices=LOCATIONS)
    last_modified = models.DateTimeField(auto_now=True)


class EventLog(models.Model):
    """Model for the event log, containing traces."""

    traces = models.ManyToManyField(Trace, related_name="event_log")
    dfg = models.ImageField(null=True)
    xes = models.FileField(null=True)
    last_modified = models.DateTimeField(auto_now=True)


class Prompt(models.Model):
    """Model for the prompt to be used in the GPT query."""

    name = models.CharField(max_length=100)
    text = models.TextField()
