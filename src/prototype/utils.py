"""Module providing constants for the project."""
import os
import time
from pathlib import Path

import openai

import prompts as p

out_path = Path("content/outputs/")  # Path to the outputs-folder
in_path = Path("content/inputs/")  # Path to the inputs-folder
oaik = os.environ.get(
    "OPENAI_API_KEY"
)  # Get the OpenAI API key from the environment variables
MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 500
TEMPERATURE_SUMMARIZING = 0
TEMPERATURE_CREATION = 1
CSV_OUTPUT = "content/outputs/intermediates/7_output.csv"
CSV_ALL_TRACES = "content/outputs/all_traces.csv"


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


""" def query_gpt(task, temperature=TEMPERATURE_SUMMARIZING, mode="zero_shot", inputs=None):
    Queries the GPT engine with given prompts in a specified mode.
    messages = query_database(task, mode)

    if inputs is not None:
        for input in inputs:
            messages[1]["content"] = messages[1]["content"] + "\n" + input
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=temperature,
    )
    output = response.choices[0].message.content
    return output """


def query_gpt(messages, temperature=TEMPERATURE_SUMMARIZING):
    """Queries the GPT engine with given prompts in a specified mode."""
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=temperature,
    )
    output = response.choices[0].message.content
    return output
