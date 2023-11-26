"""Module providing constants for the project."""
import os
from pathlib import Path
from django.conf import settings

out_path = settings.BASE_DIR / Path(
    "extraction/content/outputs/"
)  # Path to the outputs-folder
in_path = settings.BASE_DIR / Path(
    "extraction/content/inputs/"
)  # Path to the inputs-folder

oaik = os.environ.get(
    "OPENAI_API_KEY"
)  # Get the OpenAI API key from the environment variables
MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 600
TEMPERATURE = 0.5
