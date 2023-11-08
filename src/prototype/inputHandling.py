import openai
import os
import csv
import pandas as pd
import pm4py
import constants as c
import prompts as p

openai.api_key = c.oaik


def convertInpToXES(input):
    print("Converting Data: Summarizing the text.", end="\r")
    bp = convertTextToBulletpoints(input)
    print("Converting Data: Extracting date information (1/2).", end="\r")
    bp_withStart = addStartDates(input, bp)
    print("Converting Data: Extracting date information (2/2).", end="\r")
    bp_withEnd = addEndDates(input, bp_withStart)
    print("Converting Data: Creating output CSV.              ", end="\r")
    outputfile = convertBPToCSV(bp_withEnd)
    print("Converting Data: Creating output XES.              ", end="\r")
    outputfile = convertCSVToXES(outputfile)
    print("Dataconversion finished.              ")
    return outputfile


def convertTextToBulletpoints(input):
    messages = [
        {"role": "system", "content": p.TtoBP_context},
        {"role": "user", "content": p.TtoBP_prompt + input},
        {"role": "assistant", "content": p.TtoBP_answer},
    ]
    bulletpoints = openai.ChatCompletion.create(
        model=c.model,
        messages=messages,
        max_tokens=c.max_tokens,
        temperature=c.temperature,
    )
    output = bulletpoints.choices[0].message.content
    output = removeCommas(output)
    output = addEndingCommas(output)
    with open(os.path.join(c.out_path, "intermediates/bulletpoints.txt"), "w") as f:
        f.write(output)
    return output


def addStartDates(input, bp):
    messages = [
        {"role": "system", "content": p.BP_startDate_context},
        {"role": "user", "content": p.BP_startDate_prompt + input + "\n" + bp},
        {"role": "assistant", "content": p.BP_startDate_answer},
    ]
    bp_start = openai.ChatCompletion.create(
        model=c.model,
        messages=messages,
        max_tokens=c.max_tokens,
        temperature=c.temperature,
    )
    output = bp_start.choices[0].message.content
    output = removeBrackets(output)
    output = addEndingCommas(output)
    with open(
        os.path.join(c.out_path, "intermediates/bulletpoints_with_start.txt"), "w"
    ) as f:
        f.write(output)
    return output


def addEndDates(input, bp_withStart):
    messages = [
        {"role": "system", "content": p.BP_endDate_context},
        {"role": "user", "content": p.BP_endDate_prompt + input + "\n" + bp_withStart},
        {"role": "assistant", "content": p.BP_endDate_answer},
    ]
    bp_end = openai.ChatCompletion.create(
        model=c.model,
        messages=messages,
        max_tokens=c.max_tokens,
        temperature=c.temperature,
    )
    output = bp_end.choices[0].message.content
    output = removeBrackets(output)
    with open(
        os.path.join(c.out_path, "intermediates/bulletpoints_with_start_end.txt"), "w"
    ) as f:
        f.write(output)
    return output


def convertBPToCSV(bp_withEnd):
    bp_list = bp_withEnd.split("\n")
    bp_matrix = []
    for entry in bp_list:
        entry = entry.strip("- ")
        entry = entry.split(", ")
        bp_matrix.append(entry)
    fields = ["caseID", "event", "start", "end"]
    for row in bp_matrix:
        row.insert(0, 1)
    outputfile = os.path.join(c.out_path, "output.csv")
    with open(outputfile, "w") as f:
        write = csv.writer(f)
        # write.writerow(['sep=,'])
        write.writerow(fields)
        write.writerows(bp_matrix)
    return outputfile


def convertCSVToXES(inputfile):
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
def removeCommas(bp):
    bp = bp.replace(", ", "/")
    bp = bp.replace(",", "/")
    return bp


def addEndingCommas(bp):
    bp = bp.replace("\n", ",\n")
    bp = bp + ","
    return bp


def removeBrackets(bp):
    bp = bp.replace("(", "")
    bp = bp.replace(")", "")
    bp = bp.replace("]", "")
    bp = bp.replace("[", "")
    bp = bp.replace("{", "")
    bp = bp.replace("}", "")
    return bp


### Legacy Code ###

"""
def convertBulletpointsToActions(bulletPoints):
    messages = [
        {"role": "system", "content": p.convertBPtoA_task_prompt},
        {"role": "user", "content": p.convertBPtoA_label_prompt + bulletPoints}
    ]
    actions = openai.ChatCompletion.create(model=c.model, messages=messages, max_tokens=c.max_tokens, temperature=0)
    return actions.choices[0].message.content
"""
