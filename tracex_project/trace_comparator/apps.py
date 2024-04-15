"""App configuration for trace comparator app."""
from django.apps import AppConfig


class TraceTestingEnvConfig(AppConfig):
    """App configuration class for django UI."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "trace_comparator"
