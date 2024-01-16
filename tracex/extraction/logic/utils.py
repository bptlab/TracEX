"""Module providing constants for the project."""
import time
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import pm4py

from .constants import *
from openai import OpenAI


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


def query_gpt(messages, max_tokens=MAX_TOKENS, temperature=TEMPERATURE_SUMMARIZING):
    """Queries the GPT engine."""
    client = OpenAI(api_key=oaik)
    response = client.chat.completions.create(
        model=MODEL, messages=messages, max_tokens=max_tokens, temperature=temperature
    )
    output = response.choices[0].message.content
    return output


def create_xes(csv_file, name, key):
    """Creates a xes with all traces from the regarding csv."""
    dataframe = pd.read_csv(csv_file, sep=",")
    dataframe["caseID"] = dataframe["caseID"].astype(str)
    dataframe["start"] = pd.to_datetime(dataframe["start"])
    dataframe["end"] = pd.to_datetime(dataframe["end"])
    dataframe["duration"] = pd.to_timedelta(dataframe["duration"])
    dataframe = dataframe.rename(
        columns={
            key: "concept:name",
            "caseID": "case:concept:name",
            "start": "time:timestamp",
            "end": "time:endDate",
            "duration": "time:duration",
        }
    )
    output_name = name + "_" + key + ".xes"
    pm4py.write_xes(
        dataframe,
        (output_path / output_name),
        case_id_key="case:concept:name",
        activity_key="concept:name",
        timestamp_key="time:timestamp",
    )
    return str(output_path / output_name)


@dataclass
class ExtractionConfiguration:
    patient_journey: str
    event_types: list
    locations: list
    activity_key: Optional[str] = "event_type"

    def update(self, **kwargs):
        """Update the configuration with a dictionary."""
        for key, value in kwargs.items():
            setattr(self, key, value)
