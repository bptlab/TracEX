"""Module providing functions for creating a xes with all traces from the regarding csv."""
import os

import pm4py
import pandas as pd

import constants as c

KEY = "locationtype"  # Has to be "event" / "eventtype" / "locationtype"


def create_all_trace_xes(key):
    """Creates a xes with all traces from the regarding csv."""
    if key in ("event", "eventtype", "locationtype"):
        pass
    else:
        print("The activity_key has to be 'event', 'eventtype' or 'locationtype'!")
        return
    dataframe = pd.read_csv(c.CSV_ALL_TRACES, sep=",")
    dataframe["caseID"] = dataframe["caseID"].astype(str)
    dataframe["start"] = pd.to_datetime(dataframe["start"])
    dataframe["duration"] = pd.to_timedelta(dataframe["duration"])
    dataframe = dataframe.rename(
        columns={
            key: "concept:name",
            "caseID": "case:concept:name",
            "start": "time:timestamp",
            "duration": "time:duration",
        }
    )
    output_name = "all_traces_" + key + ".xes"
    pm4py.write_xes(
        dataframe,
        os.path.join(c.out_path, output_name),
        case_id_key="case:concept:name",
        activity_key="concept:name",
        timestamp_key="time:timestamp",
    )


create_all_trace_xes(KEY)
