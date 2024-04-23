"""Module providing constants for the project."""
import os
from pathlib import Path
from django.conf import settings

output_path = settings.BASE_DIR / Path(
    "extraction/content/outputs/"
)  # Path to the outputs-folder
input_path = settings.BASE_DIR / Path(
    "extraction/content/inputs/"
)  # Path to the inputs-folder
comparison_path = settings.BASE_DIR / Path(
    "extraction/content/comparison/"
)  # Path to the comparisons-folder
oaik = os.environ.get(
    "OPENAI_API_KEY"
)  # Get the OpenAI API key from the environment variables
MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1100
TEMPERATURE_SUMMARIZING = 0
TEMPERATURE_CREATION = 1
CSV_OUTPUT = settings.BASE_DIR / "extraction/content/outputs/single_trace.csv"
CSV_ALL_TRACES = settings.BASE_DIR / "extraction/content/outputs/all_traces.csv"
EVENT_TYPES = [
    ("Symptom Onset", "Symptom Onset"),
    ("Symptom Offset", "Symptom Offset"),
    ("Diagnosis", "Diagnosis"),
    ("Doctor Visit", "Doctor Visit"),
    ("Treatment", "Treatment"),
    ("Hospital Admission", "Hospital Admission"),
    ("Hospital Discharge", "Hospital Discharge"),
    ("Medication", "Medication"),
    ("Lifestyle Change", "Lifestyle Change"),
    ("Feelings", "Feelings"),
]
LOCATIONS = [
    ("Home", "Home"),
    ("Hospital", "Hospital"),
    ("Doctors", "Doctors"),
]
ACTIVITY_KEYS = [
    ("event_type", "Event Type"),
    ("activity", "Activity Label"),
    ("attribute_location", "Location"),
]
THRESHOLD_FOR_MATCH = 0.5
