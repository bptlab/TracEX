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

from extraction.models import Prompt
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
