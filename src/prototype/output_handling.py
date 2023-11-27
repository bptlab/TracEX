"""Module providing functions for printing out the XES."""
import os

import pandas as pd

import utils as u


def get_output():
    """Prints the output to the console or shows the filename."""
    if not os.path.isfile(u.CSV_OUTPUT):
        print("The output can not be read.")
        return
    decision = u.get_decision("Would you like to see the output? (y/n)\n")
    if decision:
        print("Loading output...", end="\r")
        dataframe = pd.read_csv(u.CSV_OUTPUT, sep=",")
        dataframe["start"] = pd.to_datetime(dataframe["start"])
        dataframe["end"] = pd.to_datetime(dataframe["end"])
        dataframe["duration"] = pd.to_timedelta(dataframe["duration"])
        dataframe = dataframe.rename(
            columns={
                "start": "time:timestamp",
                "end": "time:endDate",
                "duration": "time:duration",
            }
        )
        dataframe["caseID"] = dataframe["caseID"].astype(str)
        print(dataframe)
    else:
        print("The output can be found at " + u.CSV_OUTPUT + ".")
    decision = u.get_decision(
        "Would you like to append this trace to " + u.CSV_ALL_TRACES + "? (y/n)\n"
    )
    if decision:
        append_csv()


def get_output_without_user_io():
    """Prints the output to the console or shows the filename."""
    dataframe = pd.read_csv(u.CSV_OUTPUT, sep=",")
    dataframe["start"] = pd.to_datetime(dataframe["start"])
    dataframe["end"] = pd.to_datetime(dataframe["end"])
    dataframe["duration"] = pd.to_timedelta(dataframe["duration"])
    dataframe = dataframe.rename(
        columns={
            "start": "time:timestamp",
            "end": "time:endDate",
            "duration": "time:duration",
        }
    )
    dataframe["caseID"] = dataframe["caseID"].astype(str)
    print(dataframe)
    append_csv()


def append_csv():
    """Appends the current trace to the CSV containing all traces."""
    trace_count = 0
    with open(u.CSV_ALL_TRACES, "r") as f:
        rows = f.readlines()[1:]
        if len(rows) >= 2:
            trace_count = max(int(row.split(",")[0]) for row in rows if row)
    with open(u.CSV_OUTPUT, "r") as f:
        previous_content = f.readlines()
        content = []
        for row in previous_content:
            if row != "\n":
                content.append(row)
        content = content[1:]
    with open(u.CSV_ALL_TRACES, "a") as f:
        for row in content:
            row = row.replace(row[0], str(int(row[0]) + trace_count), 1)
            f.writelines(row)


def farewell():
    """Prints a farewell message."""
    print("-----------------------------------\nThank you for using TracEX!\n\n")
