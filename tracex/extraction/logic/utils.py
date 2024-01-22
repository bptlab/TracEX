"""Module providing constants for the project."""
import base64
import tempfile
import time
from dataclasses import dataclass
from io import StringIO, BytesIO
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
    """Queries the GPT API and returns a string of the output to the specified question/instruction."""
    client = OpenAI(api_key=oaik)
    response = client.chat.completions.create(
        model=MODEL, messages=messages, max_tokens=max_tokens, temperature=temperature
    )
    output = response.choices[0].message.content
    return output


def get_all_xes_output_path(
        is_test=False,
        is_extracted=False,
        xes_name="all_traces",
        activity_key="event_type",
):
    """Create the xes file for all journeys."""
    if not (is_test or is_extracted):
        append_csv()
        all_traces_xes_path = Conversion.create_xes(
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


@deprecated
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


class Conversion:
    @staticmethod
    def create_xes(csv_file, name, key):
        """Creates a xes with all traces from the regarding csv."""
        dataframe = pd.read_csv(csv_file, sep=",")
        dataframe["caseID"] = dataframe["caseID"].astype(str)
        dataframe["start"] = pd.to_datetime(dataframe["start"])
        dataframe["end"] = pd.to_datetime(dataframe["end"])
        dataframe["duration"] = pd.to_timedelta(dataframe["duration"])  # Bug: When filters are applied from the JourneyGenerationView, there seems to be some type of "offset"
        # Hence I got the error "Could not convert 'Symptom Onset' to NumPy timedelta" when deselecting "Home" from
        # This error does not appear when configuring filters in the ResultView
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

    @staticmethod
    def create_html_from_xes(df):
        """Create html table from xes file."""
        xes_html_buffer = StringIO()
        pd.DataFrame.to_html(df, buf=xes_html_buffer)
        return xes_html_buffer

    @staticmethod
    def create_dfg_png_from_df(df):
        """Create png image from xes file."""
        dfg_img_buffer = BytesIO()
        output_dfg_file = pm4py.discover_dfg(
            df, "concept:name", "time:timestamp", "case:concept:name"
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file_path = temp_file.name
            pm4py.save_vis_dfg(
                output_dfg_file[0],
                output_dfg_file[1],
                output_dfg_file[2],
                temp_file_path,
                rankdir="TB",
            )
        with open(temp_file_path, "rb") as temp_file:
            dfg_img_buffer.write(temp_file.read())
        os.remove(temp_file_path)
        dfg_img_base64 = base64.b64encode(dfg_img_buffer.getvalue()).decode("utf-8")
        return dfg_img_base64
