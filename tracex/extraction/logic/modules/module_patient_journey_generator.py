import os
import random
from datetime import datetime, timedelta

from ..module import Module
from .. import utils as u
from .. import constants as c
from .. import prompts as p

from pandas import DataFrame


class PatientJourneyGenerator(Module):
    """
    This is the module that generates a patient journey. This is primarily used for testing purposes.
    The generated patient journeys are called "synthetic patient journeys".
    """

    def __init__(self):
        super().__init__()
        self.name = "Patient Journey Generator"
        self.description = (
            "Generates a patient journey with the help of the GPT engine."
        )

    def execute(self, _input, patient_journey=None):
        # TODO: convert to dataframe
        super().execute(_input, patient_journey)
        self.result = self.__create_patient_journey()

    def __create_patient_journey(self):
        """Creates a new patient journey with the help of the GPT engine."""
        print(
            "Please wait while the system is generating a patient journey. This may take a few moments."
        )
        messages = [
            {"role": "system", "content": self.__create_patient_journey_context()},
            {"role": "user", "content": p.CREATE_PATIENT_JOURNEY_PROMPT},
        ]
        patient_journey = u.query_gpt(messages=messages, temperature=1)
        i = 0
        proposed_filename = "journey_synth_covid_" + str(i) + ".txt"
        output_path = c.input_path / proposed_filename
        while os.path.isfile(output_path):
            i += 1
            proposed_filename = "journey_synth_covid_" + str(i) + ".txt"
            output_path = c.input_path / proposed_filename
        with open(output_path, "w") as f:
            f.write(patient_journey)
        print(
            'Generation in progress: [▬▬▬▬▬▬▬▬▬▬] 100%, done! Patient journey "'
            + proposed_filename
            + '" generated.'
        )
        return patient_journey

    def __create_patient_journey_context(self):
        """Creation of a patient journey."""
        print("Generation in progress: [----------] 0%", end="\r")
        sex = "male" if random.randrange(2) == 0 else "female"
        print("Generation in progress: [▬---------] 10%", end="\r")
        country = self.__get_country()
        print("Generation in progress: [▬▬--------] 20%", end="\r")
        date = self.__get_date()
        print("Generation in progress: [▬▬▬-------] 30%", end="\r")
        life_circumstances = self.__get_life_circumstances(sex)
        print("Generation in progress: [▬▬▬▬▬-----] 50%", end="\r")
        patient_journey_context = (
            f"Imagine being a {sex} person from {country}, that was infected with Covid19."
            f" You had first symptoms on {date}. {life_circumstances}"
        )
        return patient_journey_context

    @staticmethod
    def __get_country():
        """Randomizing country."""
        european_countries = [
            "Albania",
            "Andorra",
            "Armenia",
            "Austria",
            "Azerbaijan",
            "Belarus",
            "Belgium",
            "Bosnia and Herzegovina",
            "Bulgaria",
            "Croatia",
            "Cyprus",
            "Czechia",
            "Denmark",
            "Estonia",
            "Faroe Islands",
            "Finland",
            "France",
            "Georgia",
            "Germany",
            "Greece",
            "Hungary",
            "Iceland",
            "Ireland",
            "Italy",
            "Kazakhstan",
            "Kosovo",
            "Latvia",
            "Liechtenstein",
            "Lithuania",
            "Luxembourg",
            "Malta",
            "Moldova",
            "Monaco",
            "Montenegro",
            "Netherlands",
            "North Macedonia",
            "Norway",
            "Poland",
            "Portugal",
            "Romania",
            "Russia",
            "San Marino",
            "Serbia",
            "Slovakia",
            "Slovenia",
            "Spain",
            "Sweden",
            "Switzerland",
            "Turkey",
            "Ukraine",
            "United Kingdom (UK)",
            "Vatican City (Holy See)",
        ]

        return random.choice(european_countries)

    @staticmethod
    def __get_date(start_date="01/01/2020", end_date="01/09/2023"):
        """Randomizing date."""
        start = datetime.strptime(start_date, "%d/%m/%Y")
        end = datetime.strptime(end_date, "%d/%m/%Y")
        delta = end - start
        random_days = random.randrange(delta.days)
        date = start + timedelta(days=random_days)
        date = date.strftime("%d/%m/%Y")

        return date

    @staticmethod
    def __get_life_circumstances(sex):
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
        life_circumstances = u.query_gpt(
            messages=message, max_tokens=100, temperature=1
        )
        return life_circumstances
