"""This module contains the models for the tracex database."""
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


class Trace(models.Model):
    """Model for the trace of a patient journey."""

    patient_journey = models.ForeignKey(
        PatientJourney, on_delete=models.CASCADE, related_name="trace"
    )
    last_modified = models.DateTimeField(auto_now=True)
    manager = models.Manager()

    def __str__(self):
        return f"Trace of {self.patient_journey.name} (id: {self.id})"  # pylint: disable=no-member


class Cohort(models.Model):
    """Model for the cohort of a patient journey."""

    trace = models.OneToOneField(
        Trace, on_delete=models.CASCADE, related_name="cohort", null=True
    )
    age = models.IntegerField(null=True, blank=True)
    sex = models.CharField(max_length=25, null=True, blank=True)
    origin = models.CharField(max_length=50, null=True, blank=True)
    condition = models.CharField(max_length=50, null=True, blank=True)
    preexisting_condition = models.CharField(max_length=100, null=True, blank=True)
    manager = models.Manager()

    def __str__(self):
        return f"Cohort of {self.trace.__str__().split('(')[0]} (id: {self.id})"  # pylint: disable=no-member


class Event(models.Model):
    """Django model representing a single event in a trace."""

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
    """Django model representing a prompt for a GPT query."""

    DEFAULT_NAME = ""
    DEFAULT_CATEGORY = "zero-shot"

    name = models.CharField(max_length=100, default=DEFAULT_NAME)
    category = models.CharField(max_length=100, default=DEFAULT_CATEGORY)
    text = models.JSONField()

    def __str__(self):
        return f"{self.name} (id: {self.id})"  # pylint: disable=no-member


class Metric(models.Model):
    """Django model representing metrics tracked by the metrics analyzer."""

    event = models.OneToOneField(
        Event, on_delete=models.CASCADE, related_name="metrics"
    )
    activity_relevance = models.CharField(max_length=25, null=True)
    timestamp_correctness = models.BooleanField(null=True)
    correctness_confidence = models.DecimalField(
        max_digits=3, decimal_places=2, null=True
    )
    last_modified = models.DateTimeField(auto_now=True)
    manager = models.Manager()

    def __str__(self):
        return f"Metric of {self.event.__str__().split('(')[0]} (id: {self.id})"  # pylint: disable=no-member
