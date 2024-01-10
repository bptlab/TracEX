"""Module providing functions for converting text to CSV."""
import csv

import pandas as pd

from . import utils as u
from . import prompts as p


def convert_text_to_csv(text):
    """Converts the input to CSV with intermediate steps."""
    steps = str(7)
    print("Converting Data: Summarizing the text. (1/" + steps + ")", end="\r")
    bulletpoints = convert_text_to_bulletpoints(text)
    print(
        "Converting Data: Extracting start date information. (2/" + steps + ")",
        end="\r",
    )
    u.pause_between_queries()
    start = add_start_dates(text, bulletpoints)
    print(
        "Converting Data: Extracting end date information. (3/" + steps + ")   ",
        end="\r",
    )
    u.pause_between_queries()
    end = add_end_dates(text, start)
    print(
        "Converting Data: Extracting duration information. (4/" + steps + ") ", end="\r"
    )
    u.pause_between_queries()
    duration = add_durations(text, end)
    print(
        "Converting Data: Extracting event types. (5/" + steps + ")          ", end="\r"
    )
    u.pause_between_queries()
    event_type = add_event_types(duration)
    print(
        "Converting Data: Extracting location information. (6/" + steps + ")", end="\r"
    )
    u.pause_between_queries()
    location = add_locations(event_type)
    print(
        "Converting Data: Creating output CSV. (7/" + steps + ")             ", end="\r"
    )
    output_path = convert_to_csv(location)
    print("Dataconversion finished.                    ")
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
    for i in bulletpoints:
        new_row = pd.DataFrame([i], columns=["event_information"])
        df = pd.concat([df, new_row], ignore_index=True)
    with open(
        (u.output_path / "intermediates/bulletpoints.txt"),
        "w",
    ) as f:
        f.write("\n")
    return df


def add_start_dates(text, df):
    """Adds start dates to the bulletpoints."""
    name = "start_date"
    new_df = pd.DataFrame([], columns=[name])
    list = df.values.tolist()
    i = 0
    for item in list:
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
        print(name + ": " + str(i) + "      ", end="\r")
        i = i + 1
        with open(
            (u.output_path / "intermediates/bulletpoints.txt"),
            "a",
        ) as f:
            f.write("\n" + output)
    df = pd.concat([df, new_df], axis=1)
    return df


def add_end_dates(text, df):
    """Adds end dates to the bulletpoints."""
    name = "end_date"
    new_df = pd.DataFrame([], columns=[name])
    list = df.values.tolist()
    i = 0
    for item in list:
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
        print(name + ": " + str(i) + "      ", end="\r")
        i = i + 1
        with open(
            (u.output_path / "intermediates/bulletpoints.txt"),
            "a",
        ) as f:
            f.write("\n" + output)
    df = pd.concat([df, new_df], axis=1)
    return df


def add_durations(text, df):
    """Adds durations to the bulletpoints."""
    name = "duration"
    new_df = pd.DataFrame([], columns=[name])
    list = df.values.tolist()
    i = 0
    for item in list:
        messages = [
            {"role": "system", "content": p.DURATION_CONTEXT},
            {
                "role": "user",
                "content": p.DURATION_PROMPT
                + "\nThe text: "
                + text
                + "\nThe bulletpoint: "
                + item[0]
                + "\nThe start date: "
                + item[1]
                + "\nThe end date: "
                + item[2],
            },
            {"role": "assistant", "content": p.DURATION_ANSWER},
        ]
        output = u.query_gpt(messages)

        fc_message = [
            {"role": "system", "content": p.FC_DURATION_CONTEXT},
            {"role": "user", "content": p.FC_DURATION_PROMPT + "The text: " + output},
        ]
        duration = u.query_gpt(
            fc_message,
            tool_choice={"type": "function", "function": {"name": "add_duration"}},
        )
        new_row = pd.DataFrame([duration], columns=[name])
        new_df = pd.concat([new_df, new_row], ignore_index=True)
        print(name + ": " + str(i) + "      ", end="\r")
        i = i + 1
        with open(
            (u.output_path / "intermediates/bulletpoints.txt"),
            "a",
        ) as f:
            f.write("\n" + output)
    df = pd.concat([df, new_df], axis=1)
    return df


def add_event_types(df):
    """Adds event types to the bulletpoints."""
    name = "event_type"
    new_df = pd.DataFrame([], columns=[name])
    list = df.values.tolist()
    i = 0
    for item in list:
        messages = [
            {"role": "system", "content": p.EVENT_TYPE_CONTEXT},
            {
                "role": "user",
                "content": p.EVENT_TYPE_PROMPT + "\nThe bulletpoint: " + item[0],
            },
            {"role": "assistant", "content": p.EVENT_TYPE_ANSWER},
        ]
        output = u.query_gpt(messages)

        fc_message = [
            {"role": "system", "content": p.FC_EVENT_TYPE_CONTEXT},
            {"role": "user", "content": p.FC_EVENT_TYPE_PROMPT + "The text: " + output},
        ]
        event_type = u.query_gpt(
            fc_message,
            tool_choice={"type": "function", "function": {"name": "add_event_type"}},
        )
        new_row = pd.DataFrame([event_type], columns=[name])
        new_df = pd.concat([new_df, new_row], ignore_index=True)
        print(name + ": " + str(i) + "      ", end="\r")
        i = i + 1
        with open(
            (u.output_path / "intermediates/bulletpoints.txt"),
            "a",
        ) as f:
            f.write("\n" + output)
    df = pd.concat([df, new_df], axis=1)
    return df


def add_locations(df):
    """Adds locations to the bulletpoints."""
    name = "attribute_location"
    new_df = pd.DataFrame([], columns=[name])
    list = df.values.tolist()
    event_type_key = df.columns.get_loc("event_type")
    i = 0
    for item in list:
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
        output = u.query_gpt(messages)

        fc_message = [
            {"role": "system", "content": p.FC_LOCATION_CONTEXT},
            {"role": "user", "content": p.FC_LOCATION_PROMPT + "The text: " + output},
        ]
        location = u.query_gpt(
            fc_message,
            tool_choice={"type": "function", "function": {"name": "add_location"}},
        )
        new_row = pd.DataFrame([location], columns=[name])
        new_df = pd.concat([new_df, new_row], ignore_index=True)
        print(name + ": " + str(i) + "      ", end="\r")
        i = i + 1
        with open(
            (u.output_path / "intermediates/bulletpoints.txt"),
            "a",
        ) as f:
            f.write("\n\n" + output)
    df = pd.concat([df, new_df], axis=1)
    return df


def convert_dataframe_to_csv(df):
    output_path = u.output_path / "single_trace.csv"
    df.insert(loc=0, column="case_id", value="0")
    df.to_csv(
        path_or_buf=output_path, sep=",", encoding="utf-8", header=True, index=False
    )
    return output_path
