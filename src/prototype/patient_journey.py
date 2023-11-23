# pylint: disable=import-error
"""Module providing the needed prompts for the gpt_queries."""
import random

import openai

import constants as c

openai.api_key = c.oaik


def create_patient_journey_context():
    """Creation of a patient journey."""
    print("Generation in progress: [----------] 0%", end="\r")
    sex = get_sex()
    print("Generation in progress: [▬---------] 10%", end="\r")
    country = get_country()
    print("Generation in progress: [▬▬--------] 20%", end="\r")
    date = get_date()
    print("Generation in progress: [▬▬▬-------] 30%", end="\r")
    life_circumstances = get_life_circumstances(sex)
    print("Generation in progress: [▬▬▬▬▬-----] 50%", end="\r")
    return (
        "Imagine being a "
        + sex
        + " person from "
        + country
        + ", that was infected with Covid19. You had first symptoms on "
        + date
        + "."
        + life_circumstances
    )


def get_sex():
    """Randomizing sex."""
    if random.randrange(2) == 0:
        return "male"
    return "female"


def get_country():
    """Randomizing country."""
    message = [{"role": "user", "content": "Please give me one european country."}]
    country = openai.ChatCompletion.create(
        model=c.MODEL, messages=message, max_tokens=50, temperature=0.2
    )
    return country.choices[0].message.content


def get_date():
    """Randomizing date."""
    message = [
        {
            "role": "user",
            "content": "Please give me one date between 01/01/2020 and 01/09/2023.",
        }
    ]
    country = openai.ChatCompletion.create(
        model=c.MODEL, messages=message, max_tokens=50, temperature=0.5
    )
    return country.choices[0].message.content


def get_life_circumstances(sex):
    """Randomizing life circumstances."""
    message = [{"role": "user", "content": life_circumstances_prompt(sex)}]
    life_circumstances = openai.ChatCompletion.create(
        model=c.MODEL, messages=message, max_tokens=100, temperature=1
    )
    return life_circumstances.choices[0].message.content


def life_circumstances_prompt(sex):
    """Prompt for the life circumstances randomization."""
    return (
        "Please give me a short description of the life circumstances of an imaginary "
        + sex
        + " person in form of continous text."
        + """
        Please give me a short description of the life circumstances of an imaginary "+" person in form of continous text.
        Write the text from a second-person perspective. Something like "You are a 51-year-old Teacher" and so forth.
        Inlcude the age, the job and the family status.
        Please do not include more than 50 words.
        """
    )


CREATE_PATIENT_JOURNEY_PROMPT = """
    Please outline the course of your covid19 infection, what you did (and when you did that) because of it and which doctors you may consulted.
    Please give some information about the time, in a few cases directly as a date and in the other as something in the lines of 'in the next days', 'the week after that' or similar.
    Give your outline as a continous text.
    Also include if you later went for getting a vaccine and if so, how often. You don't have to include deails about who you are.
    Please include 100 to 400 words, but not more than 400.
"""
