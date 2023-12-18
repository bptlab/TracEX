"""Module providing functions for creating a xes with all traces from the regarding csv."""
import pm4py
import pandas as pd

from . import utils as u


def get_activity_key():
    """Gets the key from the user."""
    key = input(
        "Which key should be used for the activity? (event_info/event_type/location_attribute)\n"
    ).lower()
    if key in ("event_info", "event_type", "location_attribute"):
        return key
    print("Please enter 'event_info', 'event_type', 'location_attribute'.")
    return get_activity_key()


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
        (u.output_path / output_name),
        case_id_key="case:concept:name",
        activity_key="concept:name",
        timestamp_key="time:timestamp",
    )
    return str(u.output_path / output_name)


# ACTIVITY_KEY = 'event_type' # get_key()
# create_all_trace_xes(u.CSV_OUTPUT, ACTIVITY_KEY)
