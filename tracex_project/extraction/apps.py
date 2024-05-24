"""App configuration for extraction app."""
from django.apps import AppConfig


class ExtractionConfig(AppConfig):
    """
    Configuration class for the 'extraction' Django application.

    This class allows customization of application configuration. It sets the default type of auto-created
    primary key fields to be 64-bit integers and specifies the name of the application.

    Attributes:
        default_auto_field: The type of auto-created primary key fields for models in this application.
        name: The name of the application that is being configured.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "extraction"
