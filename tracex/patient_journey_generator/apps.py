"""App configuration for patient journey generator app."""
from django.apps import AppConfig


class PatientJourneyGeneratorConfig(AppConfig):
    """App configuration class for django UI."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "patient_journey_generator"