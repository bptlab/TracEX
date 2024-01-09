"""App configuration for extraction app."""
from django.apps import AppConfig


class ExtractionConfig(AppConfig):
    """App configuration class for django UI."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "extraction"

    def ready(self):
        from extraction.logic import orchestrator
        orchestrator = orchestrator.Orchestrator()
        print("Orchestrator ready")
