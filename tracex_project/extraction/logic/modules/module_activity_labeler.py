"""This is the module that extracts the activity labels from the patient journey."""
from pathlib import Path
import pandas as pd
from django.conf import settings

from extraction.logic.module import Module
from extraction.models import Prompt
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
        self,
        _input=None,
        patient_journey=None,
        patient_journey_sentences=None,
        cohort=None,
    ):
        """
        Extracts the activity labels from the patient journey with the following steps:
        1. Number the patient journey sentences to enable selecting a specific range of sentences.
        2. Extract the activity labels from the patient journey using chatgpt.
        """
        super().execute(
            _input,
            patient_journey=patient_journey,
            patient_journey_sentences=patient_journey_sentences,
            cohort=cohort,
        )

        condition = cohort["condition"] if cohort is not None else None

        patient_journey_numbered = self.__number_patient_journey_sentences(
            patient_journey_sentences
        )
        activity_labels = self.__extract_activities(patient_journey_numbered, condition)

        return activity_labels

    @staticmethod
    def __number_patient_journey_sentences(patient_journey_sentences):
        """
        Number the patient journey sentences in the format:
            1: ...
            2: ...
        And so on.
        """
        patient_journey_numbered = patient_journey_sentences[:]
        for count, value in enumerate(patient_journey_numbered):
            patient_journey_numbered[count] = f"{count}: {value}"
        patient_journey_numbered = "\n".join(patient_journey_numbered)

        return patient_journey_numbered

    @staticmethod
    def __extract_activities(patient_journey_numbered, condition):
        """
        Converts a patient journey, where every sentence is numbered, to a DataFrame with the activity labels by
        extracting the activity labels from the patient journey.
        """
        column_name = "activity"
        messages = Prompt.objects.get(name="TEXT_TO_ACTIVITY_MESSAGES").text

        if condition is not None:
            messages.append(
                {
                    "role": "user",
                    "content": f"Focus on those events that are related to the course of the disease of {condition}."
                    f"\n\n{patient_journey_numbered}",
                }
            )
        else:
            messages.append({"role": "user", "content": patient_journey_numbered})
        activity_labels = u.query_gpt(messages).split("\n")
        df = pd.DataFrame(activity_labels, columns=[column_name])
        df[["activity", "sentence_id"]] = df["activity"].str.split(" #", expand=True)

        return df
