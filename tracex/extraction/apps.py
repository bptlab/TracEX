"""App configuration for extraction app."""
import os

from django.apps import AppConfig
from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration


class ExtractionConfig(AppConfig):
    """App configuration class for django UI."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "extraction"

    def ready(self):
        """Initialize the orchestrator before entering the first view"""
        if os.environ.get('RUN_MAIN'):
            orchestrator_instance = Orchestrator()
            orchestrator_instance.set_configuration(ExtractionConfiguration())
            print("Orchestrator ready")
