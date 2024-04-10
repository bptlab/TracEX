"""This module contains the models for the extraction app."""
from django.db import models

from tracex.logic.constants import EVENT_TYPES, LOCATIONS


class PatientJourney(models.Model):
    """Model for the patient journey input."""

    name = models.CharField(
        max_length=100,
        help_text="The name represents a unique title describing the content of the patient journey.",
        unique=True,
    )
    patient_journey = models.TextField()
    manager = models.Manager()

    def __str__(self):
        return f"{self.name} (id: {self.id})"  # pylint: disable=no-member


class Cohort(models.Model):
    """Model for the Cohort of a patient journey."""

    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=25, null=True)
    origin = models.CharField(max_length=50, null=True)
    condition = models.CharField(max_length=50, null=True)
    preexisting_condition = models.CharField(max_length=100, null=True)
    manager = models.Manager()

    def __str__(self):
        return f"Cohort of {self.trace.__str__()} (id: {self.id})"  # pylint: disable=no-member


class Trace(models.Model):
    """Model for a single trace, belonging to a patient journey."""

    patient_journey = models.ForeignKey(
        PatientJourney, on_delete=models.CASCADE, related_name="trace"
    )
    cohort = models.ForeignKey(
        Cohort, on_delete=models.CASCADE, related_name="trace", null=True, blank=True
    )
    last_modified = models.DateTimeField(auto_now=True)
    manager = models.Manager()

    def __str__(self):
        return f"Trace of {self.patient_journey.name} (id: {self.id})"  # pylint: disable=no-member


class Event(models.Model):
    """Model for a single event, only relevant in context with other events belonging to the same trace."""

    trace = models.ForeignKey(Trace, on_delete=models.CASCADE, related_name="events")
    activity = models.TextField()
    event_type = models.CharField(max_length=25, choices=EVENT_TYPES)
    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.DurationField()
    location = models.CharField(max_length=25, choices=LOCATIONS)
    last_modified = models.DateTimeField(auto_now=True)
    manager = models.Manager()

    def __str__(self):
        return f"Event of {self.trace.__str__().split('(')[0]} (id: {self.id})"  # pylint: disable=no-member


class Prompt(models.Model):
    """Model for the prompt to be used in the GPT query."""

    name = models.CharField(max_length=100)
    text = models.TextField()
