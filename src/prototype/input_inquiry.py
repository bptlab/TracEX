"""Module providing functions for the input inquiry of the prototype."""
import os
import openai

import constants as c
import prompts as p

openai.api_key = c.oaik

"""Prints a greeting message."""""
def greeting():
    print(
        "\n\nWelcome to the prototype of TracEX!\n-----------------------------------"
    )

"""Gets the input from the user."""
def get_input():
    input_path = get_input_path()
    if input_path == "new":
        inp = create_patient_journey()
    else:
        with open(os.path.join(c.in_path, input_path), encoding="utf-8") as f:
            inp = f.read()
    return inp

"""Gets the path to the input file from the user."""""
def get_input_path():
    awnser = input(
        "Would you like to continue with an existing patient journey as .txt? (y/n)\n"
    ).lower()
    if awnser == "y":
        return get_input_path_name()
    if awnser == "n":
        return "new"
    else:
        print("Please enter y or n.")
        return get_input_path()

"""Gets the name of the input file from the user."""
def get_input_path_name():
    filename = input(
        "Please enter the name of the .txt file (located in 'content/inputs/'):\n"
    )
    if filename[-4:] != ".txt":
        filename += ".txt"
    if not os.path.isfile(os.path.join(c.in_path, filename)):
        print("File does not exist.")
        return get_input_path_name()
    return filename

"""Creates a new patient journey with the help of the GPT-3 engine."""
def create_patient_journey():
    print(
        "Please wait while the system is generating a patient journey. This may take a few moments."
    )
    messages = [
        {"role": "system", "content": p.create_patient_journey_context()},
        {"role": "user", "content": p.create_patient_journey_prompt},
    ]
    patient_journey = openai.ChatCompletion.create(
        model=c.MODEL, messages=messages, max_tokens=c.MAX_TOKENS, temperature=c.TEMPERATURE
    )
    patient_journey_txt = patient_journey.choices[0].message.content
    i = 0
    proposed_filename = "journey_synth_covid_" + str(i) + ".txt"
    output_path = os.path.join(c.in_path, proposed_filename)
    while os.path.isfile(output_path):
        i += 1
        proposed_filename = "journey_synth_covid_" + str(i) + ".txt"
        output_path = os.path.join(c.in_path, proposed_filename)
    with open(output_path, "w") as f:
        f.write(patient_journey_txt)
    print(
        'Generation in progress: [▬▬▬▬▬▬▬▬▬▬] 100%, done! Patient journey "'
        + proposed_filename
        + '" generated.'
    )
    return patient_journey_txt