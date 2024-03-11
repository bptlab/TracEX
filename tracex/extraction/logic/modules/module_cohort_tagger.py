"""This is the module that cohort tags from the patient journey."""
from pathlib import Path
import pandas as pd
from django.conf import settings

from ..logging import log_execution_time
from ..module import Module
from .. import prompts as p
from .. import utils as u


class CohortTagger(Module):
    """
    This is the module that extracts the cohort tags from the patient journey.
    """

    def __init__(self):
        super().__init__()
        self.name = "Cohort Tagger"
        self.description = "Extracts the cohort tags from a patient journey."

    @log_execution_time(Path(settings.BASE_DIR / "extraction/logs/execution_time.log"))
    def execute(self, df, patient_journey=None):
        super().execute(df, patient_journey)

        return self.__extract_cohort_tags(df)

    def __extract_cohort_tags(self, df):
        """Converts the input text to activity_labels."""
        self.__extract_illness(self.patient_journey)
        # self.__extract_gender(self.patient_journey)
        # self.__extract_age(self.patient_journey)
        # self.__extract_origin(self.patient_journey)
        # self.__extract_previous_illnesses(self.patient_journey)
        return df

    def __write_cohort_tag(tag):
        """Writes the cohort tag to an intermediate file."""
        if tag[:7] == "Illness":
            with open(u.output_path / "cohort_tag.txt", "w") as f:
                f.write(tag)
        else:
            with open(u.output_path / "cohort_tag.txt", "a") as f:
                f.write(tag)

    def __extract_illness(self):
        """Extracts the illness from the patient journey."""
        messages = [
            {"role": "system", "content": p.ILLNESS_COHORT_TAG_CONTEXT},
            {
                "role": "user",
                "content": f"{p.ILLNESS_COHORT_TAG_PROMPT} {self.patient_journey}",
            },
            {"role": "assistant", "content": p.ILLNESS_COHORT_TAG_ANSWER},
        ]
        illness = u.query_gpt(messages)
        self.__write_cohort_tag("Illness: " + illness + "\n")

    def __extract_gender(self):
        """Extracts the gender from the patient journey."""
        messages = [
            {"role": "system", "content": p.TXT_TO_ACTIVITY_CONTEXT},
            {
                "role": "user",
                "content": f"{p.TXT_TO_ACTIVITY_PROMPT} {self.patient_journey}",
            },
            {"role": "assistant", "content": p.TXT_TO_ACTIVITY_ANSWER},
        ]
        gender = u.query_gpt(messages)
