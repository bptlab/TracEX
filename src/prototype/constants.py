"""Module providing constants for the project."""
import os
from pathlib import Path

out_path = Path("content/outputs/")  # Path to the outputs-folder
in_path = Path("content/inputs/")  # Path to the inputs-folder
oaik = os.environ.get(
    "OPENAI_API_KEY"
)  # Get the OpenAI API key from the environment variables
MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1000
TEMPERATURE_SUMMARIZING = 0
TEMPERATURE_CREATION = 1
XES_OUTPUT = "content/outputs/intermediates/7_output.xes"
CSV_OUTPUT = "content/outputs/intermediates/6_output.csv"
CSV_ALL_TRACES = "content/outputs/all_traces.csv"
