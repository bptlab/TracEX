# pylint: disable=import-error
# pylint: disable=unspecified-encoding
"""Module providing functions for converting text to XES."""
import os
import csv

import pm4py
import openai
import pandas as pd

import constants as c
import prompts as p

openai.api_key = c.oaik


def convert_inp_to_xes(inp):
    """Converts the input to XES with intermediate steps."""
    convertion_steps = 7
    print(
        "Converting Data: Summarizing the text. (1/" + str(convertion_steps) + ")",
        end="\r",
    )
    bulletpoints = convert_text_to_bulletpoints(inp)
    print(
        "Converting Data: Extracting date information. (2/"
        + str(convertion_steps)
        + ")",
        end="\r",
    )
    bulletpoints_start = add_start_dates(inp, bulletpoints)
    print(
        "Converting Data: Extracting duration information. (3/"
        + str(convertion_steps)
        + ")",
        end="\r",
    )
    bulletpoints_duration = add_durations_up(inp, bulletpoints_start)
    print(
        "Converting Data: Extracting event types. (4/"
        + str(convertion_steps)
        + ")          ",
        end="\r",
    )
    bulletpoints_event_type = add_event_types(bulletpoints_duration)
    print(
        "Converting Data: Extracting location information. (5/"
        + str(convertion_steps)
        + ")",
        end="\r",
    )
    bulletpoints_location = add_locations(bulletpoints_event_type)
    print(
        "Converting Data: Creating output CSV. (6/"
        + str(convertion_steps)
        + ")             ",
        end="\r",
    )
    csv_output_file = convert_bulletpoints_to_csv(bulletpoints_location)
    print(
        "Converting Data: Creating output XES. (7/" + str(convertion_steps) + ")",
        end="\r",
    )
    convert_csv_to_xes(csv_output_file)
    print("Dataconversion finished.              ")


def convert_text_to_bulletpoints(inp):
    """Converts the input text to bulletpoints."""
    messages = [
        {"role": "system", "content": p.TXT_TO_BULLETPOINTS_CONTEXT},
        {"role": "user", "content": p.TXT_TO_BULLETPOINTS_PROMPT + inp},
        {"role": "assistant", "content": p.TXT_TO_BULLETPOINTS_ANSWER},
    ]
    bulletpoints = openai.ChatCompletion.create(
        model=c.MODEL,
        messages=messages,
        max_tokens=c.MAX_TOKENS,
        temperature=c.TEMPERATURE_SUMMARIZING,
    )
    output = bulletpoints.choices[0].message.content
    output = remove_commas(output)
    output = add_ending_commas(output)
    with open(os.path.join(c.out_path, "intermediates/1_bulletpoints.txt"), "w") as f:
        f.write(output)
    return output


def add_start_dates(inp, bulletpoints):
    """Adds start dates to the bulletpoints."""
    messages = [
        {"role": "system", "content": p.BULLETPOINTS_START_DATE_CONTEXT},
        {
            "role": "user",
            "content": p.BULLETPOINTS_START_DATE_PROMPT + inp + "\n" + bulletpoints,
        },
        {"role": "assistant", "content": p.BULLETPOINTS_START_DATE_ANSWER},
    ]
    bulletpoints_start = openai.ChatCompletion.create(
        model=c.MODEL,
        messages=messages,
        max_tokens=c.MAX_TOKENS,
        temperature=c.TEMPERATURE_SUMMARIZING,
    )
    output = bulletpoints_start.choices[0].message.content
    output = add_ending_commas(output)
    with open(
        os.path.join(c.out_path, "intermediates/2_bulletpoints_with_start.txt"),
        "w",
    ) as f:
        f.write(output)
    return output


def add_durations(inp, bulletpoints_start):
    """Adds durations to the bulletpoints."""
    messages = [
        {"role": "system", "content": p.BULLETPOINTS_DURATION_CONTEXT},
        {
            "role": "user",
            "content": p.BULLETPOINTS_DURATION_PROMPT + inp + "\n" + bulletpoints_start,
        },
        {"role": "assistant", "content": p.BULLETPOINTS_DURATION_ANSWER},
    ]
    bulletpoints_start_duration = openai.ChatCompletion.create(
        model=c.MODEL,
        messages=messages,
        max_tokens=c.MAX_TOKENS,
        temperature=c.TEMPERATURE_SUMMARIZING,
    )
    output = bulletpoints_start_duration.choices[0].message.content
    output = add_ending_commas(output)
    with open(
        os.path.join(c.out_path, "intermediates/3_bulletpoints_with_duration.txt"),
        "w",
    ) as f:
        f.write(output)
    return output


def add_durations_up(inp, bulletpoints_start):
    """Adds durations to the bulletpoints."""
    messages = [
        {"role": "system", "content": p.duration_c},
        {
            "role": "user",
            "content": p.duration_p + inp + "\n" + bulletpoints_start,
        },
        {"role": "assistant", "content": p.duration_a},
    ]
    bulletpoints_start_duration = openai.ChatCompletion.create(
        model=c.MODEL,
        messages=messages,
        max_tokens=c.MAX_TOKENS,
        temperature=c.TEMPERATURE_SUMMARIZING,
    )
    output = bulletpoints_start_duration.choices[0].message.content
    output = add_ending_commas(output)
    with open(
        os.path.join(c.out_path, "intermediates/3_bulletpoints_with_duration.txt"),
        "w",
    ) as f:
        f.write(output)
    return output


def add_event_types(bulletpoints_durations):
    """Adds event types to the bulletpoints."""
    messages = [
        {"role": "system", "content": p.BULLETPOINTS_EVENT_TYPE_CONTEXT},
        {
            "role": "user",
            "content": p.BULLETPOINTS_EVENT_TYPE_PROMPT + bulletpoints_durations,
        },
        {"role": "assistant", "content": p.BULLETPOINTS_EVENT_TYPE_ANSWER},
    ]
    bulletpoints_start_duration_event_type = openai.ChatCompletion.create(
        model=c.MODEL,
        messages=messages,
        max_tokens=c.MAX_TOKENS,
        temperature=c.TEMPERATURE_SUMMARIZING,
    )
    output = bulletpoints_start_duration_event_type.choices[0].message.content
    output = add_ending_commas(output)
    with open(
        os.path.join(c.out_path, "intermediates/4_bulletpoints_with_event_type.txt"),
        "w",
    ) as f:
        f.write(output)
    return output


def add_locations(bulletpoints_event_types):
    """Adds locations to the bulletpoints."""
    messages = [
        {"role": "system", "content": p.BULLETPOINTS_LOCATION_CONTEXT},
        {
            "role": "user",
            "content": p.BULLETPOINTS_LOCATION_PROMPT + bulletpoints_event_types,
        },
        {"role": "assistant", "content": p.BULLETPOINTS_LOCATION_ANSWER},
    ]
    bulletpoints_start_duration_event_type_location = openai.ChatCompletion.create(
        model=c.MODEL,
        messages=messages,
        max_tokens=c.MAX_TOKENS,
        temperature=c.TEMPERATURE_SUMMARIZING,
    )
    output = bulletpoints_start_duration_event_type_location.choices[0].message.content
    output = remove_brackets(output)
    with open(
        os.path.join(c.out_path, "intermediates/5_bulletpoints_with_location.txt"),
        "w",
    ) as f:
        f.write(output)
    return output


def convert_bulletpoints_to_csv(bulletpoints_start_end):
    """Converts the bulletpoints to a CSV file."""
    bulletpoints_list = bulletpoints_start_end.split("\n")
    bulletpoints_matrix = []
    for entry in bulletpoints_list:
        entry = entry.strip("- ")
        entry = entry.split(", ")
        bulletpoints_matrix.append(entry)
    fields = ["caseID", "event", "start", "duration", "eventtype", "locationtype"]
    for row in bulletpoints_matrix:
        row.insert(0, 1)
    outputfile = os.path.join(c.out_path, "intermediates/6_output.csv")
    with open(outputfile, "w") as f:
        write = csv.writer(f)
        # write.writerow(['sep=,'])
        write.writerow(fields)
        write.writerows(bulletpoints_matrix)
    return outputfile


def convert_csv_to_xes(inputfile):
    """Converts the CSV file to XES."""
    dataframe = pd.read_csv(inputfile, sep=",")
    dataframe["start"] = pd.to_datetime(dataframe["start"])
    dataframe["duration"] = pd.to_timedelta(dataframe["duration"])
    dataframe = dataframe.rename(
        columns={
            "start": "time:timestamp",
            "duration": "time:duration",
        }
    )
    dataframe["caseID"] = dataframe["caseID"].astype(str)
    outputfile = os.path.join(c.out_path, "intermediates/7_output.xes")
    pm4py.write_xes(
        dataframe,
        outputfile,
        case_id_key="caseID",
        activity_key="event",
        timestamp_key="time:timestamp",
    )
    return outputfile


# Datacleaning
def remove_commas(bulletpoints):
    """Removes commas from within the bulletpoints."""
    bulletpoints = bulletpoints.replace(", ", "/")
    bulletpoints = bulletpoints.replace(",", "/")
    return bulletpoints


def add_ending_commas(bulletpoints):
    """Adds commas at the end of each line."""
    bulletpoints = bulletpoints.replace("\n", ",\n")
    bulletpoints = bulletpoints + ","
    return bulletpoints


def remove_brackets(bulletpoints):
    """Removes brackets from within the bulletpoints."""
    bulletpoints = bulletpoints.replace("(", "")
    bulletpoints = bulletpoints.replace(")", "")
    bulletpoints = bulletpoints.replace("]", "")
    bulletpoints = bulletpoints.replace("[", "")
    bulletpoints = bulletpoints.replace("{", "")
    bulletpoints = bulletpoints.replace("}", "")
    return bulletpoints
