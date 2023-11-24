# pylint: disable=import-error
# pylint: disable=unspecified-encoding
"""Module providing functions for converting text to XES."""
import csv
import os

import openai
import pandas as pd
import pm4py

from . import constants as c
from . import prompts as p

openai.api_key = c.oaik


def convert_inp_to_xes(inp):
    """Converts the input to XES with intermediate steps."""
    print("Converting Data: Summarizing the text.", end="\r")
    bulletpoints = convert_text_to_bulletpoints(inp)
    print("Converting Data: Extracting date information (1/2).", end="\r")
    bulletpoints_start = add_start_dates(inp, bulletpoints)
    print("Converting Data: Extracting date information (2/2).", end="\r")
    bulletpoints_start_end = add_end_dates(inp, bulletpoints_start)
    print("Converting Data: Creating output CSV.              ", end="\r")
    output_file = convert_bulletpoints_to_csv(bulletpoints_start_end)
    print("Converting Data: Creating output XES.              ", end="\r")
    output_file = convert_csv_to_xes(output_file)
    print("Dataconversion finished.              ")
    return output_file


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
        temperature=c.TEMPERATURE,
    )
    output = bulletpoints.choices[0].message.content
    output = remove_commas(output)
    output = add_ending_commas(output)
    with open(os.path.join(c.out_path, "intermediates/bulletpoints.txt"), "w") as f:
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
        temperature=c.TEMPERATURE,
    )
    output = bulletpoints_start.choices[0].message.content
    output = remove_brackets(output)
    output = add_ending_commas(output)
    with open(
        os.path.join(c.out_path, "intermediates/bulletpoints_with_start.txt"),
        "w",
    ) as f:
        f.write(output)
    return output


def add_end_dates(inp, bulletpoints_start):
    """Adds end dates to the bulletpoints."""
    messages = [
        {"role": "system", "content": p.BULLETPOINTS_END_DATE_CONTEXT},
        {
            "role": "user",
            "content": p.BULLETPOINTS_END_DATE_PROMPT + inp + "\n" + bulletpoints_start,
        },
        {"role": "assistant", "content": p.BULLETPOINTS_END_DATE_ANSWER},
    ]
    bulletpoints_start_end = openai.ChatCompletion.create(
        model=c.MODEL,
        messages=messages,
        max_tokens=c.MAX_TOKENS,
        temperature=c.TEMPERATURE,
    )
    output = bulletpoints_start_end.choices[0].message.content
    output = remove_brackets(output)
    with open(
        os.path.join(c.out_path, "intermediates/bulletpoints_with_start_end.txt"),
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
    fields = ["caseID", "event", "start", "end"]
    for row in bulletpoints_matrix:
        row.insert(0, 1)
    outputfile = os.path.join(c.out_path, "output.csv")
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
    dataframe["end"] = pd.to_datetime(dataframe["end"])
    dataframe = dataframe.rename(
        columns={
            "event": "concept:Activity",
            "start": "date:StartDate",
            "end": "date:EndDate",
        }
    )
    dataframe["caseID"] = dataframe["caseID"].astype(str)
    outputfile = os.path.join(c.out_path, "output.xes")
    pm4py.write_xes(dataframe, outputfile, case_id_key="caseID")
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
