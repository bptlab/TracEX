"""
Provide various utility functions for the project.

Functions:
query_gpt -- Send a request to the OPENAI API and return the response.
get_snippet_bounds -- Extract bounds for a snippet for a given activity index.

Classes:
Conversion -- Groups all functions related to conversions of DataFrames.
DataFrameUtilities -- Groups all functions related to DataFrame operations.
"""
import os
from io import StringIO
from pathlib import Path

import base64
import tempfile
import pandas as pd
import pm4py
import numpy as np

from django.conf import settings
from django.db.models import Q
from openai import OpenAI
from tracex.logic.logger import log_tokens_used
from tracex.logic.constants import (
    MAX_TOKENS,
    TEMPERATURE_SUMMARIZING,
    MODEL,
    OAIK,
)

from extraction.models import Trace


def query_gpt(
    messages,
    max_tokens=MAX_TOKENS,
    temperature=TEMPERATURE_SUMMARIZING,
    return_linear_probability=False,
    top_logprobs=None,
):
    """
    Make a request to the OPENAI API.

    Makes a request to the OPENAI API with a custom interface to the chat completion endpoint.

    Positional Arguments:
    messages -- List of messages to send to the GPT engine. Messages must bein the following format:
                [{"role": "system", "content": "text"}, {"role": "user", "content": "text"}]
                For more information see https://platform.openai.com/docs/api-reference/chat.

    Keyword Arguments:
    max_tokens -- Maximum number of tokens allowed for a single OPENAI API request. Default is specified as a constant.
    temperature -- Temperature parameter for the OPENAI API requests. Default is specified as a constant.
    return_linear_probability -- Boolean flag to return linear probabilities. Default is False.
    top_logprobs -- An integer between 0 and 5 specifying the number of most likely tokens
                    to return at each token position, each with an associated log probability.
                     return_linear_probability must be set to true if this parameter is used.

    Returns the chat completions response from the OPENAI API. Additionally, if return_linear_probability is True,
    returns the linear probability of the output.
    """

    @log_tokens_used(Path(settings.BASE_DIR / "tracex/logs/tokens_used.log"))
    def make_api_call():
        """Queries the GPT engine."""
        client = OpenAI(api_key=OAIK)
        _response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            logprobs=return_linear_probability,
            top_logprobs=top_logprobs,
        )

        return _response

    response = make_api_call()

    if return_linear_probability:
        top_logprobs = response.choices[0].logprobs.content[0].top_logprobs
        content = response.choices[0].message.content

        # Calculate the linear probability from the logarithmic probability
        # Equation: linear_probability = exp(logarithmic_probability) with 2 decimal places
        linear_probability = np.round(np.exp(top_logprobs[0].logprob), 2)

        return content, linear_probability

    output = response.choices[0].message.content

    return output


def get_snippet_bounds(index, length):
    """
    Calculate bounds for a sliding window to better extract time information.

    The sliding window ranges from the current index -2 to the current index +2. Additional logic is to ensure that
    bounds do not exceed the boundaries of the list.

    Positional Arguments:
    index -- Index of the activity in a list of sentences.
    length -- Length of the list of sentences.

    Returns the lower and upper bounds for the snippet.
    """
    half_snippet_size = min(max(2, length // 20), 5)
    lower_bound = max(0, index - half_snippet_size)
    upper_bound = min(length, index + half_snippet_size + 1)

    # Adjust the bounds if they exceed the boundaries of the list.
    if index < half_snippet_size:
        upper_bound += abs(index - half_snippet_size)
    if index > length - half_snippet_size:
        lower_bound -= abs(index - (length - half_snippet_size))

    return lower_bound, upper_bound


class Conversion:
    """
    Groups all functions related to conversions of DataFrames.

    Public Methods:
    prepare_df_for_xes_conversion -- Ensures that all requirements for the XES conversion are met.
    rename_columns -- Renames columns in a DataFrame to make them more descriptive when displayed on a webpage.
    create_html_table_from_df -- Create HTML table from DataFrame.
    create_dfg_from_df -- Create directly-follows-graph as a PNG image from a dataframe.
    dataframe_to_xes -- Converts a dataframe to a XES file.
    """

    @staticmethod
    def prepare_df_for_xes_conversion(df: pd.DataFrame, activity_key):
        """
        Renames the column that is defined as the activity key to "concept:name".

        This convention is required by the PM4PY library for the conversion of a DataFrame to a XES file. The column
        "case:concept:name" is converted to a string to ensure that the XES file is correctly generated.

        Positional Arguments:
        df -- Dataframe that is prepared for the XES conversion.
        activity_key -- Column that is defined as the activity key.
                        The activity key specifies the class that groups events in the directly-follows-graph.

        Returns the DataFrame with the renamed columns.
        """
        df_renamed = df.rename(
            columns={
                activity_key: "concept:name",
            },
            inplace=False,
        )
        df_renamed["case:concept:name"] = df["case:concept:name"].astype(str)

        return df_renamed

    @staticmethod
    def rename_columns(df: pd.DataFrame):
        """Renames columns in a DataFrame to make them more descriptive when displayed on a webpage."""
        column_mapping = {
            # rename event columns
            "case:concept:name": "Case ID",
            "activity": "Activity",
            "event_type": "Event Type",
            "time:timestamp": "Start Timestamp",
            "time:end_timestamp": "End Timestamp",
            "time:duration": "Duration",
            "attribute_location": "Location",
            "activity_relevance": "Activity Relevance",
            "timestamp_correctness": "Timestamp Correctness",
            "correctness_confidence": "Correctness Confidence",
            # rename trace columns
            "age": "Age",
            "sex": "Sex",
            "origin": "Origin",
            "condition": "Condition",
            "preexisting_condition": "Preexisting Condition",
            "trace": "Case ID",
        }

        existing_columns = {}
        for old_column, new_column in column_mapping.items():
            if old_column in df.columns:
                existing_columns[old_column] = new_column
        df_renamed = df.rename(columns=existing_columns, inplace=False)

        return df_renamed

    @staticmethod
    def create_html_table_from_df(df: pd.DataFrame):
        """Create HTML table from DataFrame."""
        df_renamed = Conversion.rename_columns(df)

        if "Start Timestamp" in df_renamed.columns:
            df_renamed.sort_values(by="Start Timestamp", inplace=True)

        html_buffer = StringIO()
        df_renamed.to_html(buf=html_buffer, index=False)

        return html_buffer.getvalue()

    @staticmethod
    def create_dfg_from_df(df: pd.DataFrame, activity_key):
        """
        Create directly-follows-graph as a PNG image from a dataframe.

        Positional Arguments:
        df -- Dataframe that is used to create the directly-follows-graph.
        activity_key -- Column that is defined as the activity key.
                        The activity key specifies the class that groups events in the directly-follows-graph.

        Returns the directly-follows-graph as a PNG image in base64 encoding.
        """
        df_renamed = Conversion.prepare_df_for_xes_conversion(
            df, activity_key=activity_key
        )
        output_dfg = pm4py.discover_dfg(
            df_renamed, "concept:name", "time:timestamp", "case:concept:name"
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            pm4py.save_vis_dfg(
                output_dfg[0],
                output_dfg[1],
                output_dfg[2],
                temp_file.name,
                rankdir="TB",
            )
            temp_file.seek(0)
            image_data = temp_file.read()

        return base64.b64encode(image_data).decode("utf-8")

    @staticmethod
    def dataframe_to_xes(df: pd.DataFrame, name, activity_key):
        """Converts a dataframe to a XES file.

        Positional Arguments:
        df -- Dataframe that is converted to a XES file.
        name -- Name of the XES file.
        activity_key -- Column that is defined as the activity key.
                        The activity key specifies the class that groups events in the directly-follows-graph.

        Returns the path to the XES file.
        """
        df_renamed = Conversion.prepare_df_for_xes_conversion(
            df, activity_key=activity_key
        )
        df_renamed.sort_values(by="time:timestamp", inplace=True)
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, f"{name}.xes")
        pm4py.objects.log.exporter.xes.exporter.apply(
            df_renamed,
            file_path,
            parameters={
                "case_id_key": "case:concept:name",
                "timestamp_key": "time:timestamp",
            },
        )

        return file_path


class DataFrameUtilities:
    """
    Groups all functions related to DataFrame operations.

    Public Methods:
    get_events_df -- Query events from the database.
    filter_dataframe -- Filter a DataFrame using a dictionary with column names.
    set_default_timestamps -- Set default timestamps for the trace if the time_extraction module didn't run.
    """

    @staticmethod
    def get_events_df(query: Q = None) -> pd.DataFrame:
        """
        Query events from the database.

        Keyword Arguments:
        query -- Query to filter the events. Default is None. This will return all events in the database.

        Returns a DataFrame with the queried events.
        """
        traces = Trace.manager.filter(query) if query else Trace.manager.all()
        if not traces.exists():
            return pd.DataFrame()  # Return an empty dataframe if no traces are found

        event_data = []

        for trace in traces:
            for event in trace.events.all():
                event_dict = {
                    "case:concept:name": trace.id,
                    "activity": event.activity,
                    "event_type": event.event_type,
                    "time:timestamp": event.start,
                    "time:end_timestamp": event.end,
                    "time:duration": event.duration,
                    "attribute_location": event.location,
                    "activity_relevance": event.metrics.activity_relevance,
                    "timestamp_correctness": event.metrics.timestamp_correctness,
                    "correctness_confidence": event.metrics.correctness_confidence,
                }

                event_data.append(event_dict)

        events_df = pd.DataFrame(event_data)

        if not events_df.empty:
            events_df = events_df.sort_values(by="time:timestamp", inplace=False)

        return events_df

    @staticmethod
    def filter_dataframe(df: pd.DataFrame, filter_dict: dict) -> pd.DataFrame:
        """
        Filter a DataFrame using a dictionary with column names.

        The filter_dict contains the column names as keys and the values to filter for as values. If a key in the
        filter_dict does not match a column in the DataFrame, there will be no filtering for this key.

        Positional Arguments:
        df -- DataFrame that is filtered.
        filter_dict -- Dictionary with column names and values to filter for.

        Returns a DataFrame where columns that are specified in the filter_dict only contain
        the values specified in the filter_dict. Columns not specified in the filter_dict are unchanged.
        """
        filter_conditions = [
            df[column].isin(values)
            if column in df.columns
            else pd.Series(True, index=df.index)
            for column, values in filter_dict.items()
        ]
        combined_condition = pd.Series(True, index=df.index)

        for condition in filter_conditions:
            combined_condition &= condition

        return df[combined_condition]

    @staticmethod
    def set_default_timestamps(df: pd.DataFrame) -> pd.DataFrame:
        """Set default timestamps for the trace if the time_extraction module didn't run."""
        df["time:timestamp"] = df.apply(
            lambda row: f"2020{str(row.name // 28 + 1).zfill(2)}{str(row.name % 28 + 1).zfill(2)}T0001",
            axis=1,
        )
        df["time:timestamp"] = pd.to_datetime(
            df["time:timestamp"], format="%Y%m%dT%H%M", errors="coerce"
        )
        df["time:end_timestamp"] = df.apply(
            lambda row: f"2020{str(row.name // 28 + 1).zfill(2)}{str(row.name % 28 + 1).zfill(2)}T0002",
            axis=1,
        )
        df["time:end_timestamp"] = pd.to_datetime(
            df["time:end_timestamp"], format="%Y%m%dT%H%M", errors="coerce"
        )
        df["time:duration"] = "00:01:00"
