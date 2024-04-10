"""This is the module that cohort tags from the patient journey."""
from pathlib import Path
from django.conf import settings

from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u
from ..module import Module
from .. import prompts as p
from ...models import Cohort


class CohortTagger(Module):
    """
    This is the module that extracts the cohort tags from the patient journey.
    """

    def __init__(self):
        super().__init__()
        self.name = "Cohort Tagger"
        self.description = "Extracts the cohort tags from a patient journey."

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute(self, df, patient_journey=None, patient_journey_sentences=None):
        super().execute(df, patient_journey, patient_journey_sentences)

        return self.__extract_cohort_tags()

    def __extract_cohort_tags(self):
        """Extracts information about condition, gender, age, origin and preexisting condition."""
        cohort_data = {}
        for message_list in p.COHORT_TAG_MESSAGES:
            messages = message_list[1:]
            messages.append(
                {"role": "user", "content": self.patient_journey},
            )
            tag = u.query_gpt(messages)
            cohort_data[message_list[0]] = tag

        valid_cohort_data = {
            key: value for key, value in cohort_data.items() if value != "N/A"
        }

        # if all values are "N/A" there is no use in saving the results
        # return 0 indicates to the calling function, that there is no Cohort
        # it expects a database id and 0 is not a valid id
        if not any(value != "NA" for value in valid_cohort_data.values()):
            return 0
        new_cohort = Cohort.manager.create(**valid_cohort_data)

        return new_cohort.pk
