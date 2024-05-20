"""The patient journey generator creates a synthetic patient journey with the help of the GPT engine."""
from datetime import datetime, timedelta
import random

from extraction.models import Prompt
from tracex.logic import utils as u
from tracex.logic import constants as c


def generate_patient_journey():
    """Creates a new patient journey with the help of the GPT engine."""
    print(
        "Please wait while the system is generating a patient journey. This may take a few moments."
    )
    messages = Prompt.objects.get(name="CREATE_PATIENT_JOURNEY").text
    messages.insert(0, {"role": "system", "content": create_patient_journey_context()})
    patient_journey = u.query_gpt(messages=messages, temperature=1)
    return patient_journey


def create_patient_journey_context():
    """Creation of a patient journey."""
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
    """Randomizing country."""

    return random.choice(c.EUROPEAN_COUNTRIES)


def get_date(start="01/01/2020", end="01/09/2023"):
    """Randomizing date."""
    start = datetime.strptime(start, "%d/%m/%Y")
    end = datetime.strptime(end, "%d/%m/%Y")
    delta = end - start
    random_days = random.randrange(delta.days)
    date = start + timedelta(days=random_days)
    date = date.strftime("%d/%m/%Y")

    return date


def get_life_circumstances(sex):
    """Randomizing life circumstances."""
    message = [
        {
            "role": "user",
            "content": f"Please give me a short description of the life circumstances of an imaginary {sex} "
            + "person in form of continuous text."
            + """Please give me a short description of the life circumstances of an imaginary person in form
                of continuous text. Write the text from a second-person perspective. Something like "You are a
                51-year-old Teacher" and so forth. Include the age, the job and the family status. Please do not
                include more than 50 words.""",
        }
    ]
    life_circumstances = u.query_gpt(messages=message, max_tokens=100, temperature=1)

    return life_circumstances
