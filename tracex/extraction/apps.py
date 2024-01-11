"""App configuration for extraction app."""
from django.apps import AppConfig
from extraction.logic import orchestrator


class ExtractionConfig(AppConfig):
    """App configuration class for django UI."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "extraction"

    def ready(self):
        orchestrator_instance = orchestrator.Orchestrator()
        orchestrator.Orchestrator._instance = orchestrator_instance
        print("Orchestrator ready")
