"""
Provides functionality to generate a synthetic Patient Journey by using the OpenAI API.

Functions:
generate_patient_journey -- Generates a synthetic Patient Journey.
create_patient_journey_context -- Creates a context for the synthetic Patient Journey.
get_country -- Randomizes a european country.
get_date -- Randomizes a start date for the synthetic Patient Journey.
get_life_circumstances -- Generates life circumstances for the synthetic Patient Journey.
"""
from datetime import datetime, timedelta
import random

from django.utils.safestring import mark_safe

from extraction.models import Prompt, PatientJourney
from tracex.logic import utils as u
from tracex.logic import constants as c


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


def generate_process_description():
    domain = "patient journeys"

    # general
    # [Symptom Onset, Symptom Offset, Diagnosis, Doctor Visit, Treatment, Hospital Admission, Hospital Discharge, Medication, Lifestyle Change, Feelings]
    event_types = "Symptom Onset, Symptom Offset, Doctor Visit, Medication"
    case_notion = "Hospital Stay"
    time_specifications = "timestamps and durations"
    writing_style = "not_similar_to_example"
    example = "I was admitted to the hospital on 01/01/2020. After a week, I was discharged. I was prescribed medication for the next two weeks."

    # domain specific
    age = 24
    sex = "female"
    occupation = "flight attendant"
    origin = "France"
    condition = "limp"
    preexisting_conditions = "none"
    persona = f"{age}-year-old {sex} {occupation} from {origin}, with the condition {condition} and the preexisting conditions {preexisting_conditions}."
    # components of the prompt
    writing_instructions = ("Please create a process description in the form of a written text of your persona. It is "
                            "important that you write an authentic, continuous text, as if written by the persona "
                            "themselves.")
    authenticity_instructions = ("Please try to consider the persona's background and the events that plausibly could "
                                 "have happened to them when creating the process description and the events that "
                                 "they talk about.")

    prompt = [
        {
            "role": "system",
            "content": "Imagine being an expert in the field of process mining. Your task is to create a process "
                       f"description within the domain of {domain}."
                       f"When creating the process description, only consider the following event types: {event_types}"
                       f"The case notion is: {case_notion}"
                       f"Include time specifications for the events as {time_specifications}."
        },
        {  # this part is meant to be the domain-specific part of the prompt
            "role": "user",
            "content": f"The persona is: {persona}" 
                       f"{writing_instructions}"
                       f"{authenticity_instructions}"
        }
    ]

    process_description = u.query_gpt(messages=prompt, temperature=1)
    print("______________________________________________________________________________________________")
    print(f"Process Description before adaptation:\n{process_description}\n")

    if writing_style == "similar_to_example":
        adaptation_prompt = [
            {
                "role": "system",
                "content": "You are an expert in writing style adaptation. Your task is to adapt the process "
                           "description so it resembles the example closely in terms of writing style while still "
                           "being authentic."
                           "It is very important that the content, especially personal information, events and temporal"
                           " specifications, remains the same, and only the style is adapted."
            },
            {
                "role": "user",
                "content": "Please adapt the process description to be more similar to the example."
                           f"Example: '{example}'"
                           f"Process Description: '{process_description}'"
            }
        ]
        process_description = u.query_gpt(messages=adaptation_prompt, temperature=0.1)

        # PatientJourney.manager.create(name="Patient Journey", patient_journey=process_description)

    return process_description


def execute_generate_process_description(number_of_instances=10):
    result = ""
    for i in range(number_of_instances):
        process_description = generate_process_description()
        result += f"<b>Process Description {i+1}:</b><br>{process_description}<br><br>"
    return mark_safe(result)
