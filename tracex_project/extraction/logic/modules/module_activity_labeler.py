"""This is the module that extracts the activity labels from the Patient Journey."""
from pathlib import Path
from typing import List, Optional
import pandas as pd
from django.conf import settings

from extraction.logic.module import Module
from extraction.models import Prompt
from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u


class ActivityLabeler(Module):
    """
    This is the module that starts the pipeline with structuring the Patient Journey in activities.
    """

    def __init__(self):
        super().__init__()
        self.name = "Activity Labeler"
        self.description = "Extracts the activity labels from a Patient Journey."

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute(
            self,
            _input=None,
            patient_journey: str = None,
            patient_journey_sentences: List[str] = None,
            cohort=None,
    ) -> pd.DataFrame:
        """
        Extracts the activity labels from the Patient Journey with the following steps:
        1. Number the Patient Journey sentences to enable selecting a specific range of sentences.
        2. Extract the activity labels from the Patient Journey using chatgpt.
        """
        super().execute(
            _input,
            patient_journey=patient_journey,
            patient_journey_sentences=patient_journey_sentences,
            cohort=cohort,
        )

        condition = getattr(cohort, "condition", None)

        patient_journey_numbered: str = self.__number_patient_journey_sentences(
            patient_journey_sentences
        )
        activity_labels: pd.DataFrame = self.__extract_activities(
            patient_journey_numbered=patient_journey_numbered,
            condition=condition,
            number_of_sentences=len(patient_journey_sentences),
        )

        return activity_labels

    @staticmethod
    def __number_patient_journey_sentences(patient_journey_sentences: List[str]) -> str:
        """
        Number the Patient Journey sentences as one String in the format:
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
    def __extract_activities(
        patient_journey_numbered: str,
        condition: Optional[str],
        number_of_sentences: int,
    ) -> pd.DataFrame:
        """
        Converts a Patient Journey, where every sentence is numbered, to a DataFrame with the activity labels by
        extracting the activity labels from the Patient Journey.
        """
        column_name = "activity"
        messages = Prompt.objects.get(name="TEXT_TO_ACTIVITY_MESSAGES").text

        user_message: str = patient_journey_numbered
        if condition is not None:
            user_message = f"Focus on those events that are related to the course of the disease of {condition}.\n\n\
            {user_message}"
        messages.append({"role": "user", "content": user_message})
        activity_labels = u.query_gpt(messages).split("\n")
        df = pd.DataFrame(activity_labels, columns=[column_name])
        try:
            df[["activity", "sentence_id"]] = df["activity"].str.split(
                " #", expand=True
            )
        except ValueError:
            scaling_factor = df.shape[0] / (number_of_sentences - 1)
            df["sentence_id"] = int(df.reset_index().index * scaling_factor)

        return df
