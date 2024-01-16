import os
import random

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

    # Remove this, only for test purposes
    def __init__(self):
        super().__init__()
        self.name = "Patient Journey Generator"
        self.description = (
            "Generates a patient journey with the help of the GPT engine."
        )
        print("PatientJourneyGenerator module is ready")

    def execute(self, _input, patient_journey=None):
        # TODO: convert to dataframe
        self.result = self.__create_patient_journey()

    @staticmethod
    def __create_patient_journey():
        """Creates a new patient journey with the help of the GPT engine."""
        print(
            "Please wait while the system is generating a patient journey. This may take a few moments."
        )
        messages = [
            {"role": "system", "content": p.create_patient_journey_context()},
            {"role": "user", "content": p.CREATE_PATIENT_JOURNEY_PROMPT},
        ]
        patient_journey_txt = u.query_gpt(messages, c.TEMPERATURE_CREATION)
        i = 0
        proposed_filename = "journey_synth_covid_" + str(i) + ".txt"
        output_path = c.input_path / proposed_filename
        while os.path.isfile(output_path):
            i += 1
            proposed_filename = "journey_synth_covid_" + str(i) + ".txt"
            output_path = c.input_path / proposed_filename
        with open(output_path, "w") as f:
            f.write(patient_journey_txt)
        print(
            'Generation in progress: [▬▬▬▬▬▬▬▬▬▬] 100%, done! Patient journey "'
            + proposed_filename
            + '" generated.'
        )
        return patient_journey_txt

    def __create_patient_journey_context(self):
        """Creation of a patient journey."""
        print("Generation in progress: [----------] 0%", end="\r")
        sex = self.__get_sex()
        print("Generation in progress: [▬---------] 10%", end="\r")
        country = self.__get_country()
        print("Generation in progress: [▬▬--------] 20%", end="\r")
        date = self.__get_date()
        print("Generation in progress: [▬▬▬-------] 30%", end="\r")
        life_circumstances = self.__get_life_circumstances(sex)
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

    @staticmethod
    def __get_sex():
        """Randomizing sex."""
        if random.randrange(2) == 0:
            return "male"
        return "female"

    @staticmethod
    def __get_country():
        """Randomizing country."""
        message = [{"role": "user", "content": "Please give me one european country."}]
        country = u.query_gpt(messages=message, max_tokens=50, temperature=0.2)
        return country

    @staticmethod
    def __get_date():
        """Randomizing date."""
        message = [
            {
                "role": "user",
                "content": "Please give me one date between 01/01/2020 and 01/09/2023.",
            }
        ]
        country = u.query_gpt(messages=message, max_tokens=50, temperature=0.5)
        return country

    def __get_life_circumstances(self, sex):
        """Randomizing life circumstances."""
        message = [{"role": "user", "content": self.__life_circumstances_prompt(sex)}]
        life_circumstances = u.query_gpt(
            messages=message, max_tokens=100, temperature=1
        )
        return life_circumstances

    @staticmethod
    def __life_circumstances_prompt(sex):
        """Prompt for the life circumstances randomization."""
        return (
            "Please give me a short description of the life circumstances of an imaginary "
            + sex
            + " person in form of continuous text."
            + """
            Please give me a short description of the life circumstances of an imaginary person in form of continuous
            text. Write the text from a second-person perspective.
            Something like "You are a 51-year-old Teacher" and so forth. Include the age, the job and the family status.
            Please do not include more than 50 words.
            """
        )
