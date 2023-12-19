"""Module providing constants for the project."""
import os
import time
from pathlib import Path
import json

import openai
import functions_calls as fc

out_path = Path("content/outputs/")  # Path to the outputs-folder
in_path = Path("content/inputs/")  # Path to the inputs-folder
oaik = os.environ.get(
    "OPENAI_API_KEY"
)  # Get the OpenAI API key from the environment variables
MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1100
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


def query_gpt(messages, tools=fc.TOOLS, tool_choice="none", temperature=TEMPERATURE_SUMMARIZING):
    """Queries the GPT engine."""
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=temperature,
        tools=tools,
        tool_choice=tool_choice,
    )
    if tool_choice == "none":
        output = response.choices[0].message.content
    else:
        output = response
        # response = json.loads(response['choices'][0]['message']['tool_calls'][0]['function']['arguments'])
        # output = response['output']
    return output
