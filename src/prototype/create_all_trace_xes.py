"""Module providing functions for creating a xes with all traces from the regarding csv."""
import os

import pm4py
import pandas as pd

import utils as u


def get_key():
    """Gets the key from the user."""
    key = input(
        "Which key should be used for the activity? (event/eventtype/locationtype)\n"
    ).lower()
    if key in ("event", "eventtype", "locationtype"):
        return key
    print("Please enter 'event', 'eventtype' or 'locationtype'.")
    return get_key()


def create_all_trace_xes(key):
    """Creates a xes with all traces from the regarding csv."""
    dataframe = pd.read_csv(u.CSV_ALL_TRACES, sep=",")
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
    output_name = "all_traces_" + key + ".xes"
    pm4py.write_xes(
        dataframe,
        os.path.join(u.out_path, output_name),
        case_id_key="case:concept:name",
        activity_key="concept:name",
        timestamp_key="time:timestamp",
    )


KEY = get_key()
create_all_trace_xes(KEY)
