"""Module providing functions for converting text to CSV."""
from datetime import datetime

import pandas as pd

from . import utils as u
from . import prompts as p


def convert_text_to_csv(text):
    """Converts the input to CSV with intermediate steps."""
    steps = str(7)
    print("Converting Data: Summarizing the text. (1/" + steps + ")", end="\r")
    dataframe = convert_text_to_bulletpoints(text)
    print(
        "Converting Data: Extracting start date information. (2/" + steps + ")",
        end="\r",
    )
    u.pause_between_queries()
    dataframe = add_start_dates(text, dataframe)
    print(
        "Converting Data: Extracting end date information. (3/" + steps + ")   ",
        end="\r",
    )
    u.pause_between_queries()
    dataframe = add_end_dates(text, dataframe)
    print(
        "Converting Data: Extracting duration information. (4/" + steps + ") ", end="\r"
    )
    u.pause_between_queries()
    dataframe = add_durations(dataframe)
    print(
        "Converting Data: Extracting event types. (5/" + steps + ")          ", end="\r"
    )
    u.pause_between_queries()
    dataframe = add_event_types(dataframe)
    print(
        "Converting Data: Extracting location information. (6/" + steps + ")", end="\r"
    )
    u.pause_between_queries()
    dataframe = add_locations(dataframe)
    print(
        "Converting Data: Creating output CSV. (7/" + steps + ")             ", end="\r"
    )
    output_path = convert_dataframe_to_csv(dataframe)
    print("Dataconversion finished.                    ")
    output_csv(dataframe)
    return output_path


def convert_text_to_bulletpoints(text):
    """Converts the input text to bulletpoints."""
    messages = [
        {"role": "system", "content": p.TEXT_TO_EVENTINFORMATION_CONTEXT},
        {"role": "user", "content": p.TEXT_TO_EVENTINFORMATION_PROMPT + text},
        {"role": "assistant", "content": p.TEXT_TO_EVENTINFORMATION_ANSWER},
    ]
    bulletpoints = u.query_gpt(messages)
    df = pd.DataFrame([], columns=["event_information"])
    bulletpoints = bulletpoints.replace("- ", "")
    bulletpoints = bulletpoints.split("\n")
    for row in bulletpoints:
        new_row = pd.DataFrame([row], columns=["event_information"])
        df = pd.concat([df, new_row], ignore_index=True)
    document_intermediates("\n", True)
    return df


def add_start_dates(text, df):
    """Adds start dates to the bulletpoints."""
    name = "start_date"
    new_df = pd.DataFrame([], columns=[name])
    values_list = df.values.tolist()
    for item in values_list:
        messages = [
            {"role": "system", "content": p.START_DATE_CONTEXT},
            {
                "role": "user",
                "content": p.START_DATE_PROMPT
                + "\nThe text: "
                + text
                + "\nThe bulletpoint: "
                + item[0],
            },
            {"role": "assistant", "content": p.START_DATE_ANSWER},
        ]
        output = u.query_gpt(messages)
        fc_message = [
            {"role": "system", "content": p.FC_START_DATE_CONTEXT},
            {"role": "user", "content": p.FC_START_DATE_PROMPT + "The text: " + output},
        ]
        start_date = u.query_gpt(
            fc_message,
            tool_choice={"type": "function", "function": {"name": "add_start_dates"}},
        )
        new_row = pd.DataFrame([start_date], columns=[name])
        new_df = pd.concat([new_df, new_row], ignore_index=True)
        row_count = new_df.shape[0]
        if start_date == "N/A" and row_count > 1:
            last_index = new_df.index[-1]
            previous_index = last_index - 1
            new_df.at[last_index, "start_date"] = new_df.at[
                previous_index, "start_date"
            ]
        document_intermediates(output)
    df = pd.concat([df, new_df], axis=1)
    return df


def add_end_dates(text, df):
    """Adds end dates to the bulletpoints."""
    name = "end_date"
    new_df = pd.DataFrame([], columns=[name])
    values_list = df.values.tolist()
    for item in values_list:
        messages = [
            {"role": "system", "content": p.END_DATE_CONTEXT},
            {
                "role": "user",
                "content": p.END_DATE_PROMPT
                + "\nThe text: "
                + text
                + "\nThe bulletpoint: "
                + item[0]
                + "\nThe start date: "
                + item[1],
            },
            {"role": "assistant", "content": p.END_DATE_ANSWER},
        ]
        output = u.query_gpt(messages)
        fc_message = [
            {"role": "system", "content": p.FC_END_DATE_CONTEXT},
            {"role": "user", "content": p.FC_END_DATE_PROMPT + "The text: " + output},
        ]
        end_date = u.query_gpt(
            fc_message,
            tool_choice={"type": "function", "function": {"name": "add_end_dates"}},
        )
        new_row = pd.DataFrame([end_date], columns=[name])
        new_df = pd.concat([new_df, new_row], ignore_index=True)
        document_intermediates(output)
    df = pd.concat([df, new_df], axis=1)
    return df


def add_durations(df):
    """Calculates and adds the duration for every event information."""

    def calculate_row_duration(row):
        if row["start_date"] == "N/A" or row["end_date"] == "N/A":
            return "N/A"
        start_date = datetime.strptime(row["start_date"], "%Y%m%dT%H%M")
        end_date = datetime.strptime(row["end_date"], "%Y%m%dT%H%M")
        duration = end_date - start_date
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    # create new column 'duration' and calculate the duration for every row
    df["duration"] = df.apply(calculate_row_duration, axis=1)
    return df


def add_event_types(df):
    """Adds event types to the bulletpoints."""
    name = "event_type"
    new_df = pd.DataFrame([], columns=[name])
    values_list = df.values.tolist()
    for item in values_list:
        messages = [
            {"role": "system", "content": p.EVENT_TYPE_CONTEXT},
            {
                "role": "user",
                "content": p.EVENT_TYPE_PROMPT + "\nThe bulletpoint: " + item[0],
            },
            {"role": "assistant", "content": p.EVENT_TYPE_ANSWER},
        ]
        event_type = u.query_gpt(messages)

        # fc_message = [
        #     {"role": "system", "content": p.FC_EVENT_TYPE_CONTEXT},
        #     {"role": "user", "content": p.FC_EVENT_TYPE_PROMPT + "The text: " + output},
        # ]
        # event_type = u.query_gpt(
        #     fc_message,
        #     tool_choice={"type": "function", "function": {"name": "add_event_type"}},
        # )
        new_row = pd.DataFrame([event_type], columns=[name])
        new_df = pd.concat([new_df, new_row], ignore_index=True)
        document_intermediates(event_type)
    df = pd.concat([df, new_df], axis=1)
    return df


def add_locations(df):
    """Adds locations to the bulletpoints."""
    name = "attribute_location"
    new_df = pd.DataFrame([], columns=[name])
    values_list = df.values.tolist()
    event_type_key = df.columns.get_loc("event_type")
    for item in values_list:
        print(item[0], end="\r")
        messages = [
            {"role": "system", "content": p.LOCATION_CONTEXT},
            {
                "role": "user",
                "content": p.LOCATION_PROMPT
                + item[0]
                + "\nThe category: "
                + item[event_type_key],
            },
            {"role": "assistant", "content": p.LOCATION_ANSWER},
        ]
        location = u.query_gpt(messages)

        # fc_message = [
        #     {"role": "system", "content": p.FC_LOCATION_CONTEXT},
        #     {"role": "user", "content": p.FC_LOCATION_PROMPT + "The text: " + output},
        # ]
        # location = u.query_gpt(
        #     fc_message,
        #     tool_choice={"type": "function", "function": {"name": "add_location"}},
        # )
        new_row = pd.DataFrame([location], columns=[name])
        new_df = pd.concat([new_df, new_row], ignore_index=True)
        document_intermediates(output)
    df = pd.concat([df, new_df], axis=1)
    return df


def convert_dataframe_to_csv(df):
    """Converts the dataframe to CSV and saves it on disk."""
    output_path = u.output_path / "single_trace.csv"
    df.insert(loc=0, column="case_id", value="0")
    df.to_csv(
        path_or_buf=output_path, sep=",", encoding="utf-8", header=True, index=False
    )
    document_intermediates(df, is_dataframe=True)
    return output_path


def output_csv(df):
    """Outputs the dataframe to the user."""
    decision = u.get_decision("Would you like to see the output? (y/n)\n")
    if decision:
        print(df)
    else:
        print("The output can be found at: " + u.output_path / "single_trace.csv.")
    decision = u.get_decision(
        "Would you like to append this trace to all_traces.csv? (y/n)\n"
    )
    if decision:
        append_csv()
    farewell()


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
            row = row.replace(row[0], str(int(row[0]) + trace_count + 1), 1)
            f.writelines(row)


def farewell():
    """Prints a farewell message."""
    print("-----------------------------------\nThank you for using TracEX!\n\n")


def document_intermediates(text, is_first=False, is_dataframe=False):
    """Writes the text to a file."""
    if is_dataframe:
        with open((u.output_path / "intermediates/bulletpoints.txt"), "a") as f:
            text = text.to_string(header=False, index=False)
            f.write("\n\n\n\nThe resulting Dataframe:\n\n" + text)
    if is_first:
        with open(
            (u.output_path / "intermediates/bulletpoints.txt"),
            "w",
        ) as f:
            f.write(text)
    else:
        with open(
            (u.output_path / "intermediates/bulletpoints.txt"),
            "a",
        ) as f:
            f.write("\n" + text)
