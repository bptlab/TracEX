"""This module contains the models for the extraction app."""
from django.db import models

from .logic.constants import EVENT_TYPES, LOCATIONS


class PatientJourney(models.Model):
    """Model for the patient journey input."""

    name = models.CharField(
        max_length=100,
        help_text="If no name is provided, the name of the uploaded file will be used.",
        unique=True,
    )
    patient_journey = models.FileField()
    manager = models.Manager()

    def __str__(self):
        return f"{self.name} (id: {self.id})"


class Trace(models.Model):
    """Model for a single trace, belonging to a patient journey."""

    patient_journey = models.ForeignKey(
        PatientJourney, on_delete=models.CASCADE, related_name="trace"
    )
    manager = models.Manager()

    def __str__(self):
        return f"Trace of {self.patient_journey.name} (id: {self.id})"


class Event(models.Model):
    """Model for a single event, only relevant in context with other events belonging to the same trace."""

    trace = models.ForeignKey(Trace, on_delete=models.CASCADE, related_name="events")
    event_information = models.TextField()
    event_type = models.CharField(max_length=25, choices=EVENT_TYPES)
    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.DurationField()
    location = models.CharField(max_length=25, choices=LOCATIONS)
    last_modified = models.DateTimeField(auto_now=True)
    manager = models.Manager()

    def __str__(self):
        return f"Event of {self.trace.__str__().split('(')[0]} (id: {self.id})"


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
