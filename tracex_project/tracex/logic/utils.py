"""Module providing various utility functions for the project."""
import os
from io import StringIO
from pathlib import Path
import base64
import tempfile
import functools
import warnings

import regex as re
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
    oaik,
)

from extraction.models import Trace


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


def query_gpt(
    messages,
    max_tokens=MAX_TOKENS,
    temperature=TEMPERATURE_SUMMARIZING,
    logprobs=False,
    top_logprobs=None,
):
    """Sends a request to the OpenAI API and returns the response."""

    @log_tokens_used(Path(settings.BASE_DIR / "tracex/logs/tokens_used.log"))
    def make_api_call():
        """Queries the GPT engine."""
        client = OpenAI(api_key=oaik)
        _response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            logprobs=logprobs,
            top_logprobs=top_logprobs,
        )

        return _response

    response = make_api_call()

    if logprobs:
        top_logprobs = response.choices[0].logprobs.content[0].top_logprobs
        content = response.choices[0].message.content
        return content, top_logprobs

    output = response.choices[0].message.content

    return output


def get_snippet_bounds(index, length):
    """Extract bounds for a snippet for a given activity index."""
    # We want to look at a snippet from the patient journey where we take five sentences into account
    # starting from the current sentence index -2 and ending at the current index +2
    half_snippet_size = min(max(2, length // 20), 5)
    lower_bound = max(0, index - half_snippet_size)
    upper_bound = min(length, index + half_snippet_size + 1)

    # Adjust the bounds if they exceed the boundaries of the patient journey
    if index < half_snippet_size:
        upper_bound += abs(index - half_snippet_size)
    if index > length - half_snippet_size:
        lower_bound -= abs(index - (length - half_snippet_size))

    return lower_bound, upper_bound


def calculate_linear_probability(logprob):
    """Calculates the linear probability from the log probability of the gpt output."""
    linear_prob = np.round(np.exp(logprob), 2)

    return linear_prob


class Conversion:
    """Class for all kinds of conversions"""

    @staticmethod
    def prepare_df_for_xes_conversion(df, activity_key):
        """Ensures that all requirements for the xes conversion are met."""
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
        """Renames columns in a DataFrame to enhance readability on a webpage. This function adjusts the column
        headers of a DataFrame based on a predefined mapping that aligns with user-friendly names suitable for
        display purposes."""
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
        """Create html table from DataFrame."""
        df_renamed = Conversion.rename_columns(df)

        if "Start Timestamp" in df_renamed.columns:
            df_renamed.sort_values(by="Start Timestamp", inplace=True)

        html_buffer = StringIO()
        df_renamed.to_html(buf=html_buffer, index=False)

        return html_buffer.getvalue()

    @staticmethod
    def create_dfg_from_df(df, activity_key):
        """Create png image from df."""
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
    def dataframe_to_xes(df, name, activity_key):
        """Conversion from dataframe to xes file, stored temporarily on disk."""
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

    @staticmethod
    def text_to_sentence_list(text):
        """Converts a text into a list of its sentences."""
        text = text.replace("\n", " ")
        # This regex looks for periods, question marks, or exclamation marks,
        # possibly followed by more of the same, followed by a space or end of string.
        pattern = re.compile(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)(?=\s|$)")
        sentences = pattern.split(text)
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

        return sentences


class DataFrameUtilities:
    """Class for all kinds of operations that performs on Dataframes"""

    @staticmethod
    def get_events_df(query: Q = None):
        """Get all events from the database, or filter them by a query and return them as a dataframe."""
        traces = Trace.manager.filter(query) if query else Trace.manager.all()
        if not traces.exists():
            return pd.DataFrame()  # Return an empty dataframe if no traces are found

        event_data = []

        for trace in traces:
            for event in trace.events.all():
                event_dict = {
                    "case:concept:name": trace.id,
                    "activity": event.activity,
                    "time:timestamp": event.start,
                    "time:end_timestamp": event.end,
                    "time:duration": event.duration,
                    "event_type": event.event_type,
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
    def filter_dataframe(df, filter_dict):
        """Filter a dataframe using a dictionary with column names."""
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
    def set_default_timestamps(df):
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

    @staticmethod
    def delete_metrics_columns(df):
        """Delete metrics columns from the dataframe."""
        df = df.drop(
            columns=[
                "activity_relevance",
                "timestamp_correctness",
                "correctness_confidence",
            ],
        )
