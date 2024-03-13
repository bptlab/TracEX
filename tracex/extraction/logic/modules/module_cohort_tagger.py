"""This is the module that cohort tags from the patient journey."""
from pathlib import Path
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
        self.__write_cohort_tag("Name of Journey", False)
        for message_list in p.COHORT_TAG_MESSAGES:
            messages = message_list[1:]
            messages.append(
                {"role": "user", "content": self.patient_journey},
            )
            tag = u.query_gpt(messages)
            self.__write_cohort_tag(message_list[0] + ": " + tag)
        return df

    def __write_cohort_tag(self, tag, append=True):
        """Writes the cohort tag to an intermediate file."""
        if not append:
            with open(u.output_path / "cohort_tag.txt", "w") as f:
                f.write(tag + "\n")
        else:
            with open(u.output_path / "cohort_tag.txt", "a") as f:
                f.write(tag + "\n")
