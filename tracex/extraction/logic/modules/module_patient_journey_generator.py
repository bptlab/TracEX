import os
from ..module import Module
from .. import utils as u
from .. import constants as c
from .. import prompts as p


class PatientJourneyGenerator(Module):
    def __init__(self, name, description):
        super().__init__(name, description)
        print("test2")

    def execute(self):
        text = self.create_patient_journey()
        # convert to dataframe
        return text

    @staticmethod
    def create_patient_journey():
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
