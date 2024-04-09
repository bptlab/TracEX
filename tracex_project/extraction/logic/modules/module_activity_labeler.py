"""This is the module that extracts the activity labels from the patient journey."""
from pathlib import Path
import pandas as pd
from django.conf import settings

from extraction.logic.module import Module
from extraction.logic import prompts as p
from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u


class ActivityLabeler(Module):
    """
    This is the module that extracts the activity labels from the patient journey.
    """

    def __init__(self):
        super().__init__()
        self.name = "Activity Labeler"
        self.description = "Extracts the activity labels from a patient journey."

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute(
        self, _input=None, patient_journey=None, patient_journey_sentences=None
    ):
        super().execute(_input, patient_journey, patient_journey_sentences)

        return self.__extract_activities()

    def __extract_activities(self):
        """Converts the input text to activity_labels."""
        patient_journey_numbered = self.patient_journey_sentences[:]
        for count, value in enumerate(patient_journey_numbered):
            patient_journey_numbered[count] = f"{count}: {value}"
        patient_journey_numbered = ".\n".join(patient_journey_numbered)

        name = "activity"
        messages = p.TEXT_TO_ACTIVITY_MESSAGES[:]
        messages.append({"role": "user", "content": patient_journey_numbered})
        activity_labels = u.query_gpt(messages)
        activity_labels = activity_labels.split("\n")
        df = pd.DataFrame(activity_labels, columns=[name])
        df[["activity", "sentence_id"]] = df["activity"].str.split(" #", expand=True)

        return df
