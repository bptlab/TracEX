"""
Provides functionality to generate a synthetic Patient Journey by using the OpenAI API.

Functions:
generate_patient_journey -- Generates a synthetic Patient Journey.
create_patient_journey_context -- Creates a context for the synthetic Patient Journey.
get_country -- Randomizes a european country.
get_date -- Randomizes a start date for the synthetic Patient Journey.
get_life_circumstances -- Generates life circumstances for the synthetic Patient Journey.
"""
import copy
from datetime import datetime
import random
import os
import json

from django.utils.safestring import mark_safe

from extraction.models import Prompt, PatientJourney
from tracex.logic import utils as u


def execute_generate_process_description(number_of_instances=1, degree_of_variation="low", save_to_db=False,
                                         save_as_txt=False, config=None):
    if config is None:
        with open('patient_journey_generator/process_description_configurations/patient_journey_configuration.json',
                  'r') as f:
            config = json.load(f)
        print("Using default configuration.")
    else:
        config = json.loads(config.read().decode('utf-8'))
        print("Using custom configuration.")

    result = ""
    for i in range(number_of_instances):
        process_description = generate_process_description(degree_of_variation, save_to_db, save_as_txt,
                                                           iteration=i + 1, config=config)
        result += f"<b>Process Description {i + 1}:</b><br>{process_description}<br><hr><br>"
    return mark_safe(result)


def generate_process_description(degree_of_variation="low", save_to_db=False, save_as_txt=False, iteration=0,
                                 config=None):
    # Load configuration
    config = config
    instance_config = get_instance_config(config, degree_of_variation)

    # general parameters
    domain = instance_config["domain"]
    case = instance_config["case"]
    case_notion = instance_config["case_notion"]
    event_types = instance_config["event_types"]

    # case attributes
    case_attributes_dict = instance_config["case_attributes_dict"]
    case_attributes = ', '.join(f"{key}: {value}" for key, value in case_attributes_dict.items())

    # process description attributes
    time_specifications = instance_config["time_specifications"]
    writing_style = instance_config["writing_style"]
    example = instance_config["example"]

    # instructions
    perspective_instructions = instance_config["perspective_instructions"]
    writing_instructions = instance_config["writing_instructions"]
    authenticity_instructions = instance_config["authenticity_instructions"]

    generation_prompt = [
        {
            "role": "system",
            "content": "Imagine being an expert in the field of process mining. Your task is to create a process "
                       f"description within the domain of {domain}.\n"
                       f"The case and therefore the object of the process description is: {case}.\n"
                       f"The case notion and therefore the scope of the process description is: {case_notion}.\n"
                       f"The attributes that characterize the case are: {case_attributes}.\n"
                       f"When creating the process description, only consider the following event types: {event_types}\n"
                       f"Include time specifications for the events as {time_specifications}."
        },
        {
            "role": "user",
            "content": f"{perspective_instructions}"
                       f"{writing_instructions}"
                       f"{authenticity_instructions}"
        }
    ]

    generation_prompt_temperature = instance_config["generation_prompt_temperature"]
    process_description = u.query_gpt(messages=generation_prompt, temperature=generation_prompt_temperature,
                                      model="gpt-3.5-turbo")

    if writing_style == "similar_to_example":
        adaptation_prompt = [
            {
                "role": "system",
                "content": "You are an expert in writing style adaptation. Your task is to adapt the process "
                           "description so it resembles the example closely in terms of writing style and everything "
                           "this entails while still being authentic."
                           f"It is very important that the content, especially case attributes ({case_attributes}), "
                           "events and temporal specifications, remain the same, and only the writing style is adapted."
            },
            {
                "role": "user",
                "content": "Please adapt the process description to be more similar to the example."
                           f"Example: '{example}'"
                           f"Process Description: '{process_description}'"
            }
        ]
        adaptation_prompt_temperature = instance_config["adaptation_prompt_temperature"]
        process_description = u.query_gpt(messages=adaptation_prompt, temperature=adaptation_prompt_temperature,
                                          model="gpt-3.5-turbo")

    # save process description
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    patient_journey_name = f"{timestamp}_{case}_{degree_of_variation}_{writing_style}_{iteration}"
    if save_to_db:
        PatientJourney.manager.create(name=patient_journey_name, patient_journey=process_description)
    if save_as_txt:
        directory = "patient_journey_generator/generated_process_descriptions"
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(f"{directory}/{patient_journey_name}.txt", "w") as file:
            file.write(process_description)

    # add instance configuration to process description
    process_description += f"<br><br><u>Instance Configuration:</u><br>Degree of Variation: {degree_of_variation}<br>Event Types: {event_types}<br>Case Attributes: {case_attributes}<br>Time Specifications: {time_specifications}<br>Writing Style: {writing_style}<br>"

    return process_description


def get_instance_config(config, degree_of_variation):
    instance_config = copy.deepcopy(config)

    # low degree of variation
    if degree_of_variation == "low":
        for key, value in instance_config.items():
            if key == "event_types":
                if isinstance(value, list):
                    instance_config[key] = ', '.join(value)
                    # adjustment for evaluation of process description batch with "low" degree of variation
                    # instance_config[key] = "Symptom Onset, Hospital Admission, Hospital Discharge, Symptom Offset"
            elif key == "case_attributes_dict":
                for attribute, values in value.items():
                    if isinstance(values, list):
                        instance_config[key][attribute] = values[0]
            elif isinstance(value, list):
                instance_config[key] = value[0]

        instance_config["writing_style"] = "free"
        instance_config["generation_prompt_temperature"] = 0.1
        instance_config["adaptation_prompt_temperature"] = 0.1

    # medium degree of variation
    elif degree_of_variation == "medium":
        for key, value in instance_config.items():
            if key == "event_types":
                if isinstance(value, list):
                    num_event_types = random.randint(3, len(value))
                    selected_event_types = random.sample(value, num_event_types)
                    instance_config[key] = ', '.join(selected_event_types)
            elif key == "case_attributes_dict":
                for attribute, values in value.items():
                    if isinstance(values, list):
                        instance_config[key][attribute] = random.choice(values)
            elif isinstance(value, list):
                instance_config[key] = value[0]

        instance_config["writing_style"] = "free"
        instance_config["generation_prompt_temperature"] = 0.6
        instance_config["adaptation_prompt_temperature"] = 0.6

    # high degree of variation
    elif degree_of_variation == "high":
        for key, value in instance_config.items():
            if key == "event_types":
                if isinstance(value, list):
                    num_event_types = random.randint(3, len(value))
                    selected_event_types = random.sample(value, num_event_types)
                    instance_config[key] = ', '.join(selected_event_types)
            elif key == "case_attributes_dict":
                for attribute, values in value.items():
                    if isinstance(values, list):
                        instance_config[key][attribute] = random.choice(values)
            elif isinstance(value, list):
                instance_config[key] = random.choice(value)

        instance_config["writing_style"] = "similar_to_example"
        instance_config["generation_prompt_temperature"] = 1
        instance_config["adaptation_prompt_temperature"] = 1

    return instance_config
