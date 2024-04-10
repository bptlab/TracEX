"""Module providing various utility functions for the project."""
import os
from io import StringIO, BytesIO
from pathlib import Path

import base64
import json
import tempfile
import functools
import warnings
import pandas as pd
import pm4py
import numpy as np

from pandas.api.types import is_datetime64_any_dtype as is_datetime
from django.conf import settings
from openai import OpenAI
from tracex.logic.logger import log_tokens_used
from tracex.logic.constants import (
    MAX_TOKENS,
    TEMPERATURE_SUMMARIZING,
    MODEL,
    oaik,
    output_path,
    CSV_OUTPUT,
    CSV_ALL_TRACES,
)

from . import function_calls


def deprecated(func):
    """This is a decorator which can be used to mark functions as deprecated.
    It will result in a warning being emitted when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn(
            f"Call to deprecated function {func.__name__}.",
            category=DeprecationWarning,
            stacklevel=2,
        )
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


def query_gpt(
    messages,
    max_tokens=MAX_TOKENS,
    temperature=TEMPERATURE_SUMMARIZING,
    tools=None,
    tool_choice="none",
    logprobs=False,
    top_logprobs=None,
):
    """Sends a request to the OpenAI API and returns the response."""

    tools = function_calls.TOOLS if tools is None else tools

    @log_tokens_used(Path(settings.BASE_DIR / "tracex/logs/tokens_used.log"))
    def make_api_call():
        """Queries the GPT engine."""
        client = OpenAI(api_key=oaik)
        _response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=tools,
            tool_choice=tool_choice,
            logprobs=logprobs,
            top_logprobs=top_logprobs,
        )

        return _response

    response = make_api_call()
    if tool_choice != "none":
        api_response = response.choices[0].message.tool_calls[0].function.arguments
        output = json.loads(api_response)["output"][0]

    elif logprobs:
        top_logprobs = response.choices[0].logprobs.content[0].top_logprobs
        content = response.choices[0].message.content
        return content, top_logprobs
    else:
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
            csv_file=CSV_ALL_TRACES, name=xes_name, key=activity_key
        )
    else:
        all_traces_xes_path = str(output_path / xes_name) + "_" + activity_key + ".xes"
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


def calculate_linear_probability(logprob):
    linear_prob = np.round(np.exp(logprob), 2)
    return linear_prob


class Conversion:
    """Class for all kinds of conversions"""

    @staticmethod
    def prepare_df_for_xes_conversion(df, activity_key):
        """Ensures that all requirements for the xes conversion are met."""
        df["case_id"] = df["case_id"].astype(str)
        df["start"] = pd.to_datetime(df["start"])
        df["end"] = pd.to_datetime(df["end"])
        df = df.rename(
            columns={
                activity_key: "concept:name",
                "case_id": "case:concept:name",
                "start": "start_timestamp",
                "end": "time:end_timestamp",
                "duration": "time:duration",
            }
        )
        return df

    @staticmethod
    def create_xes(csv_file, name, key):
        """Creates a xes with all traces from the regarding csv."""
        dataframe = pd.read_csv(csv_file, sep=",")
        dataframe = Conversion.prepare_df_for_xes_conversion(dataframe, key)

        output_name = name + "_" + key + ".xes"
        pm4py.write_xes(
            dataframe,
            (output_path / output_name),
            case_id_key="case:concept:name",
            activity_key="concept:name",
            start_timestamp_key="start_timestamp",
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
    def create_dfg_from_df(df):
        """Create png image from xes file."""
        dfg_img_buffer = BytesIO()
        output_dfg_file = pm4py.discover_dfg(
            df, "concept:name", "start_timestamp", "case:concept:name"
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

    @staticmethod
    def align_df_datatypes(source_df, target_df):
        """Aligns the datatypes of two dataframes."""
        for column in source_df.columns:
            if column in target_df.columns and not is_datetime(source_df[column].dtype):
                source_df[column] = source_df[column].astype(target_df[column].dtype)
            elif is_datetime(source_df[column].dtype):
                source_df[column] = source_df[column].dt.tz_localize(tz=None)
        return source_df
