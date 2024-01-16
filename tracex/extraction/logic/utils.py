"""Module providing constants for the project."""
import time
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import pm4py

from .constants import *
from openai import OpenAI


import functools
import warnings


def deprecated(func):
    """This is a decorator which can be used to mark functions as deprecated.
    It will result in a warning being emitted when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn(f"Call to deprecated function {func.__name__}.",
                      category=DeprecationWarning,
                      stacklevel=2)
        return func(*args, **kwargs)
    return new_func


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


def get_all_xes_output_path(
        is_test=False,
        is_extracted=False,
        xes_name="all_traces",
        activity_key="event_type",
):
    """Create the xes file for all journeys."""
    if not (is_test or is_extracted):
        append_csv()
        all_traces_xes_path = create_xes(
            CSV_ALL_TRACES, name=xes_name, key=activity_key
        )
    else:
        all_traces_xes_path = (
                str(output_path / xes_name) + "_" + activity_key + ".xes"
        )
    return all_traces_xes_path


def append_csv():
    """Appends the current trace to the CSV containing all traces."""
    trace_count = 0
    with open(CSV_ALL_TRACES, "r") as f:
        rows = f.readlines()[1:]
        if len(rows) >= 2:
            trace_count = max(int(row.split(",")[0]) for row in rows if row)
    with open(CSV_OUTPUT, "r") as f:
        previous_content = f.readlines()
        content = []
        for row in previous_content:
            if row != "\n":
                content.append(row)
        content = content[1:]
    with open(CSV_ALL_TRACES, "a") as f:
        for row in content:
            row = row.replace(row[0], str(int(row[0]) + trace_count), 1)
            f.writelines(row)


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
