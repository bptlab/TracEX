"""Module providing various utility functions for the project."""
import os
from io import StringIO, BytesIO
from pathlib import Path

import base64
import tempfile
import functools
import warnings
import pandas as pd
import pm4py
import numpy as np

from pandas.api.types import is_datetime64_any_dtype as is_datetime
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from openai import OpenAI
from tracex.logic.logger import log_tokens_used
from tracex.logic.constants import (
    MAX_TOKENS,
    TEMPERATURE_SUMMARIZING,
    MODEL,
    oaik,
    output_path,
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
        df["case:concept:name"] = df["case:concept:name"].astype(str)
        df = df.rename(
            columns={
                activity_key: "concept:name",
            }
        )

        return df

    @staticmethod
    def create_html_table_from_df(df: pd.DataFrame):
        """Create html table from DataFrame."""
        html_buffer = StringIO()
        df.to_html(
            buf=html_buffer,
            columns=df.drop(columns=["start_timestamp"]).columns,
            index=False,
        )

        return html_buffer.getvalue()

    @staticmethod
    def create_dfg_from_df(df):
        """Create png image from df."""
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

    @staticmethod
    def align_df_datatypes(source_df, target_df):
        """Aligns the datatypes of two dataframes."""
        for column in source_df.columns:
            if column in target_df.columns and not is_datetime(source_df[column].dtype):
                source_df[column] = source_df[column].astype(target_df[column].dtype)
            elif is_datetime(source_df[column].dtype):
                source_df[column] = source_df[column].dt.tz_localize(tz=None)

        return source_df

    @staticmethod
    def dataframe_to_xes(df, name):
        """Conversion from dataframe to xes file."""

        # Sorting Dataframe for start timestamp
        df = df.groupby("case:concept:name", group_keys=False, sort=False).apply(
            lambda x: x.sort_values(by="time:timestamp", inplace=False)
        )

        # Converting DataFrame to XES
        xes_file = output_path / name
        pm4py.write_xes(
            log=df,
            file_path=xes_file,
            case_id_key="case:concept:name",
            timestamp_key="time:timestamp",
        )

        return xes_file


class DataFrameUtilities:
    """Class for all kinds of operations that performs on Dataframes"""

    @staticmethod
    def get_events_df(query: Q = None):
        """Get all events from the database, or filter them by a query and return them as a dataframe."""
        traces = Trace.manager.all() if query is None else Trace.manager.filter(query)

        if not traces.exists():
            raise ObjectDoesNotExist("No traces match the provided query.")

        event_data = []

        for trace in traces:
            events = trace.events.all()
            for event in events:
                event_data.append(
                    {
                        "case:concept:name": trace.id,
                        "activity": event.activity,
                        "event_type": event.event_type,
                        "time:timestamp": event.start,
                        "time:end_timestamp": event.end,
                        "time:duration": event.duration,
                        "attribute_location": event.location,
                    }
                )
        events_df = pd.DataFrame(event_data)

        return events_df.sort_values(by="time:timestamp", inplace=False)

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
