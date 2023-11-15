# pylint: disable=import-error
"""Module providing functions for printing out the XES."""
import os

import pm4py

import constants as c


def get_output(inp_file_name):
    """Prints the output to the console or shows the filename."""
    if not os.path.isfile(c.XES_OUTPUT):
        print("The output can not be read.")
        return
    log = pm4py.read_xes(c.XES_OUTPUT)
    decision = get_decision("Would you like to see the output? (y/n)\n")
    if decision:
        print("Loading output...", end="\r")
        df = pm4py.convert_to_dataframe(log)
        print(df)
    else:
        print("The output can be found at " + c.XES_OUTPUT + ".")
    output_file_name = "xes/" + inp_file_name[:-4] + ".xes"
    output_file_name = os.path.join(c.out_path, output_file_name)
    if os.path.isfile(output_file_name):
        print("A trace of that journey is already saved.")
        decision = get_decision("Overwrite and append either way? (y/n)\n")
    else:
        decision = get_decision(
            "Would you like to save it and append this trace to "
            + c.CSV_ALL_TRACES
            + "? (y/n)\n"
        )
    if decision:
        pm4py.write_xes(log, output_file_name)
        append_csv()


def append_csv():
    """Appends the current trace to the CSV containing all traces."""
    trace_count = 0
    with open(c.CSV_ALL_TRACES, "r") as f:
        rows = f.readlines()[1:]
        if len(rows) >= 2:
            trace_count = max(int(row.split(",")[0]) for row in rows if row)
    with open(c.CSV_OUTPUT, "r") as f:
        previous_content = f.readlines()
        content = []
        for row in previous_content:
            if row != "\n":
                content.append(row)
        content = content[1:]
    with open(c.CSV_ALL_TRACES, "a") as f:
        for row in content:
            row = row.replace(row[0], str(int(row[0]) + trace_count), 1)
            f.writelines(row)


def get_decision(question):
    """Gets a decision from the user."""
    decision = input(question).lower()
    if decision == "y":
        return True
    if decision == "n":
        return False
    print("Please enter y or n.")
    return get_decision(question)


def farewell():
    """Prints a farewell message."""
    print("-----------------------------------\nThank you for using TracEX!\n\n")
