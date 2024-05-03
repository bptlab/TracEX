"""This is the module that cohort tags from the patient journey."""
from pathlib import Path
from django.conf import settings

from extraction.models import Cohort, Prompt
from extraction.logic.module import Module
from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u


class CohortTagger(Module):
    """
    This is the module that extracts the cohort tags from the patient journey.
    """

    def __init__(self):
        super().__init__()
        self.name = "Cohort Tagger"
        self.description = "Extracts the cohort tags from a patient journey."

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute_and_save(self, df, patient_journey=None, patient_journey_sentences=None):
        """
        Extracts the cohort from the patient journey and saves the result in the database.
        """
        super().execute_and_save(
            df,
            patient_journey=patient_journey,
            patient_journey_sentences=patient_journey_sentences
        )

        cohort_tags = self.__extract_cohort_tags(patient_journey)
        cohort_pk = self.__save_to_db(cohort_tags)

        return cohort_pk

    @staticmethod
    def __extract_cohort_tags(patient_journey):
        """Extracts information about condition, gender, age, origin and preexisting condition."""
        cohort_data = {}
        for message_list in Prompt.objects.get(name="COHORT_TAG_MESSAGES").text:
            messages = message_list[1:]
            messages.append(
                {"role": "user", "content": patient_journey},
            )
            tag = u.query_gpt(messages)
            cohort_data[message_list[0]] = tag

        return cohort_data

    @staticmethod
    def __save_to_db(cohort_data):
        """Saves the cohort tags to the database."""
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
