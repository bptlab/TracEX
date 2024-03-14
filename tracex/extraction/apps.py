"""App configuration for extraction app."""
from django.apps import AppConfig


class ExtractionConfig(AppConfig):
    """App configuration class for django UI."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "extraction"

    def ready(self):
        """Initialize the orchestrator before entering the first view"""
        orchestrator_instance = Orchestrator()
        orchestrator_instance.set_configuration(ExtractionConfiguration())
        print("Orchestrator ready")
