"""Module providing constants for the project."""
import os
import time
from pathlib import Path
from django.conf import settings

import openai

out_path = settings.BASE_DIR / Path("extraction/content/outputs/")  # Path to the outputs-folder
in_path = settings.BASE_DIR / Path("extraction/content/inputs/")  # Path to the inputs-folder
oaik = os.environ.get(
    "OPENAI_API_KEY"
)  # Get the OpenAI API key from the environment variables
MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1100
TEMPERATURE_SUMMARIZING = 0
TEMPERATURE_CREATION = 1
CSV_OUTPUT = (settings.BASE_DIR / "extraction/content/outputs/intermediates/7_output.csv")
CSV_ALL_TRACES = (settings.BASE_DIR / "extraction/content/outputs/all_traces.csv")


def pause_between_queries():
    """Pauses between queries."""
    time.sleep(5)


def get_decision(question):
    """Gets a decision from the user."""
    decision = input(question).lower()
    if decision == "y":
        return True
    if decision == "n":
        return False
    print("Please enter y or n.")
    return get_decision(question)


def query_gpt(messages, temperature=TEMPERATURE_SUMMARIZING):
    """Queries the GPT engine."""
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=temperature,
    )
    output = response.choices[0].message.content
    return output
