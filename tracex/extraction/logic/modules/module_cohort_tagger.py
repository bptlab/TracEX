"""This is the module that cohort tags from the patient journey."""
from pathlib import Path
from django.conf import settings

from tracex.logic.logging import log_execution_time
from ..module import Module
from .. import prompts as p
from tracex.logic import utils as u
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
    def execute_and_save(self, df, patient_journey=None):
        super().execute(df, patient_journey)

        return self.__extract_cohort_tags()

    def __extract_cohort_tags(self):
        """Converts the input text to activity_labels."""
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

        # if all values are "N/A" ther is no use in saving the results
        # return 0 indicates to the calling function, that there is no Cohort
        # it expects a database id and 0 is not a valid id
        if not any(value != "NA" for value in valid_cohort_data.values()):
            return 0
        new_cohort = Cohort.manager.create(**valid_cohort_data)

        return new_cohort.pk
