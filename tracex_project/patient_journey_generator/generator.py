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
from datetime import datetime, timedelta
import random
import time
import os

from django.utils.safestring import mark_safe

from extraction.models import Prompt, PatientJourney
from tracex.logic import utils as u
from tracex.logic import constants as c
from patient_journey_generator.process_description_configs import PATIENT_JOURNEY_CONFIG, ORDER_CONFIG, \
    PATIENT_JOURNEY_CONFIG_MC


def generate_patient_journey():
    """Generate a synthetic Patient Journey."""
    messages = Prompt.objects.get(name="CREATE_PATIENT_JOURNEY").text
    messages.insert(0, {"role": "system", "content": create_patient_journey_context()})
    patient_journey = u.query_gpt(messages=messages, temperature=1)

    return patient_journey


def create_patient_journey_context():
    """
    Create a context for the Patient Journey.

    The context includes a random sex, country, date and life circumstances.
    """
    sex = "male" if random.randrange(2) == 0 else "female"
    country = get_country()
    date = get_date()
    life_circumstances = get_life_circumstances(sex)
    patient_journey_context = (
        f"Imagine being a {sex} person from {country}, that was infected with Covid19."
        f" You had first symptoms on {date}. {life_circumstances}"
    )
    return patient_journey_context


def get_country():
    """Randomize a european country."""

    return random.choice(c.EUROPEAN_COUNTRIES)


def get_date(start="01/01/2020", end="01/09/2023"):
    """Get a random date between a start and end date."""
    start = datetime.strptime(start, "%d/%m/%Y")
    end = datetime.strptime(end, "%d/%m/%Y")
    delta = end - start
    random_days = random.randrange(delta.days)
    date = start + timedelta(days=random_days)
    date = date.strftime("%d/%m/%Y")

    return date


def get_life_circumstances(sex):
    """Generate life circumstances by using the OpenAI API."""
    messages = Prompt.objects.get(name="CREATE_PATIENT_JOURNEY_LIFE_CIRCUMSTANCES").text
    messages[0]["content"] = messages[0]["content"].replace("<SEX>", sex)
    life_circumstances = u.query_gpt(messages=messages, max_tokens=100, temperature=1)

    return life_circumstances


# [Symptom Onset, Symptom Offset, Diagnosis, Doctor Visit, Treatment, Hospital Admission, Hospital Discharge, Medication, Lifestyle Change, Feelings]
def generate_process_description(degree_of_variety="low", save_to_db=False, iteration=0):
    # Load configuration
    config = PATIENT_JOURNEY_CONFIG_MC
    # config = ORDER_CONFIG

    instance_config = get_instance_config(config, degree_of_variety)

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
        {  # this part is meant to be the domain-specific part of the prompt
            "role": "user",
            "content": f"{perspective_instructions}"
                       f"{writing_instructions}"
                       f"{authenticity_instructions}"
        }
    ]

    generation_prompt_temperature = instance_config["generation_prompt_temperature"]
    process_description = u.query_gpt(messages=generation_prompt, temperature=generation_prompt_temperature, model="gpt-3.5-turbo")
    print(f"Process Description before adaptation:\n{process_description}\n")

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
        process_description = u.query_gpt(messages=adaptation_prompt, temperature=adaptation_prompt_temperature, model="gpt-3.5-turbo")

    if save_to_db:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        patient_journey_name = f"{timestamp}_{case}_{degree_of_variety}_{writing_style}_{iteration}"
        PatientJourney.manager.create(name=patient_journey_name, patient_journey=process_description)

    process_description += f"<br><u>Config:</u><br>Degree of Variety: {degree_of_variety}<br>Event Types: {event_types}<br>Case Attributes: {case_attributes}<br>time_specifications: {time_specifications}<br>writing_style: {writing_style}<br>"

    return process_description


def execute_generate_process_description(number_of_instances=10, degree_of_variety="high", save_to_db=True):
    result = ""
    for i in range(number_of_instances):
        process_description = generate_process_description(degree_of_variety, save_to_db, iteration=i + 1)
        result += f"<b>Process Description {i + 1}:</b><br>{process_description}<br><br>"
    return mark_safe(result)


def get_instance_config(config, degree_of_variety):
    instance_config = copy.deepcopy(config)

    # low degree of variety
    if degree_of_variety == "low":
        for key, value in instance_config.items():
            if key == "event_types":
                if isinstance(value, list):
                    instance_config[key] = ', '.join(value)
            elif key == "case_attributes_dict":
                for attribute, values in value.items():
                    if isinstance(values, list):
                        instance_config[key][attribute] = values[0]
            elif isinstance(value, list):
                instance_config[key] = value[0]

        instance_config["writing_style"] = "free"
        instance_config["generation_prompt_temperature"] = 0.1
        instance_config["adaptation_prompt_temperature"] = 0.1

    # medium degree of variety
    elif degree_of_variety == "medium":
        for key, value in instance_config.items():
            if key == "event_types":
                if isinstance(value, list):
                    num_event_types = random.randint(3, len(value))  # Randomly select the number of event types
                    selected_event_types = random.sample(value, num_event_types)  # Randomly select the event types
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

    # high degree of variety
    elif degree_of_variety == "high":
        for key, value in instance_config.items():
            if key == "event_types":
                if isinstance(value, list):
                    num_event_types = random.randint(3, len(value))  # Randomly select the number of event types
                    selected_event_types = random.sample(value, num_event_types)  # Randomly select the event types
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
