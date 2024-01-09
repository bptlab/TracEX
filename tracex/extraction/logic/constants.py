import os
from pathlib import Path
from django.conf import settings

output_path = settings.BASE_DIR / Path(
    "extraction/content/outputs/"
)  # Path to the outputs-folder
input_path = settings.BASE_DIR / Path(
    "extraction/content/inputs/"
)  # Path to the inputs-folder
oaik = os.environ.get(
    "OPENAI_API_KEY"
)  # Get the OpenAI API key from the environment variables
MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1100
TEMPERATURE_SUMMARIZING = 0
TEMPERATURE_CREATION = 1
CSV_OUTPUT = settings.BASE_DIR / "extraction/content/outputs/intermediates/7_output.csv"
CSV_ALL_TRACES = settings.BASE_DIR / "extraction/content/outputs/all_traces.csv"
