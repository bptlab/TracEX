"""Module providing functions for converting text to CSV."""
import os
import csv
import time

import openai

import utils as u
import prompts as p

openai.api_key = u.oaik


def convert_text_to_csv(inp):
    """Converts the input to CSV with intermediate steps."""
    steps = str(7)
    print("Converting Data: Summarizing the text. (1/" + steps + ")", end="\r")
    bulletpoints = convert_text_to_bulletpoints(inp)
    print(
        "Converting Data: Extracting start date information. (2/" + steps + ")",
        end="\r",
    )
    time.sleep(5)
    bulletpoints_start = add_start_dates(inp, bulletpoints)
    print(
        "Converting Data: Extracting end date information. (3/" + steps + ")   ",
        end="\r",
    )
    time.sleep(5)
    bulletpoints_end = add_end_dates(inp, bulletpoints_start)
    print(
        "Converting Data: Extracting duration information. (4/" + steps + ") ", end="\r"
    )
    time.sleep(5)
    bulletpoints_duration = add_durations(inp, bulletpoints_end)
    print(
        "Converting Data: Extracting event types. (5/" + steps + ")          ", end="\r"
    )
    time.sleep(5)
    bulletpoints_event_type = add_event_types(bulletpoints_duration)
    print(
        "Converting Data: Extracting location information. (6/" + steps + ")", end="\r"
    )
    time.sleep(5)
    bulletpoints_location = add_locations(bulletpoints_event_type)
    print(
        "Converting Data: Creating output CSV. (7/" + steps + ")             ", end="\r"
    )
    convert_bulletpoints_to_csv(bulletpoints_location)
    print("Dataconversion finished.                    ")


def convert_text_to_bulletpoints(inp):
    """Converts the input text to bulletpoints."""
    messages = [
        {"role": "system", "content": p.TXT_TO_BULLETPOINTS_CONTEXT},
        {"role": "user", "content": p.TXT_TO_BULLETPOINTS_PROMPT + inp},
        {"role": "assistant", "content": p.TXT_TO_BULLETPOINTS_ANSWER},
    ]
    bulletpoints = u.query_gpt(messages)
    bulletpoints = remove_commas(bulletpoints)
    bulletpoints = add_ending_commas(bulletpoints)
    with open(os.path.join(u.out_path, "intermediates/1_bulletpoints.txt"), "w") as f:
        f.write(bulletpoints)
    return bulletpoints


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
    bulletpoints_start = u.query_gpt(messages)
    bulletpoints_start = add_ending_commas(bulletpoints_start)
    with open(
        os.path.join(u.out_path, "intermediates/2_bulletpoints_with_start.txt"),
        "w",
    ) as f:
        f.write(bulletpoints_start)
    return bulletpoints_start


def add_end_dates(inp, bulletpoints):
    """Adds start dates to the bulletpoints."""
    messages = [
        {"role": "system", "content": p.BULLETPOINTS_END_DATE_CONTEXT},
        {
            "role": "user",
            "content": p.BULLETPOINTS_END_DATE_PROMPT + inp + "\n" + bulletpoints,
        },
        {"role": "assistant", "content": p.BULLETPOINTS_END_DATE_ANSWER},
    ]
    bulletpoints_start = u.query_gpt(messages)
    bulletpoints_start = add_ending_commas(bulletpoints_start)
    with open(
        os.path.join(u.out_path, "intermediates/3_bulletpoints_with_end.txt"),
        "w",
    ) as f:
        f.write(bulletpoints_start)
    return bulletpoints_start


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
    bulletpoints_duration = u.query_gpt(messages)
    bulletpoints_duration = add_ending_commas(bulletpoints_duration)
    with open(
        os.path.join(u.out_path, "intermediates/4_bulletpoints_with_duration.txt"),
        "w",
    ) as f:
        f.write(bulletpoints_duration)
    return bulletpoints_duration


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
    bulletpoints_event_type = u.query_gpt(messages)
    bulletpoints_event_type = add_ending_commas(bulletpoints_event_type)
    with open(
        os.path.join(u.out_path, "intermediates/5_bulletpoints_with_event_type.txt"),
        "w",
    ) as f:
        f.write(bulletpoints_event_type)
    return bulletpoints_event_type


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
    bulletpoints_location = u.query_gpt(messages)
    bulletpoints_location = remove_brackets(bulletpoints_location)
    with open(
        os.path.join(u.out_path, "intermediates/6_bulletpoints_with_location.txt"),
        "w",
    ) as f:
        f.write(bulletpoints_location)
    return bulletpoints_location


def convert_bulletpoints_to_csv(bulletpoints_start_end):
    """Converts the bulletpoints to a CSV file."""
    bulletpoints_list = bulletpoints_start_end.split("\n")
    bulletpoints_matrix = []
    for entry in bulletpoints_list:
        entry = entry.strip("- ")
        entry = entry.split(", ")
        bulletpoints_matrix.append(entry)
    fields = [
        "caseID",
        "event_information",
        "start",
        "end",
        "duration",
        "event_type",
        "attribute_location",
    ]
    for row in bulletpoints_matrix:
        row.insert(0, 1)
    outputfile = u.CSV_OUTPUT
    with open(outputfile, "w") as f:
        write = csv.writer(f)
        # write.writerow(['sep=,'])
        write.writerow(fields)
        write.writerows(bulletpoints_matrix)
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
