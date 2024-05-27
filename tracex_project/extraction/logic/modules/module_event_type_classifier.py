"""This module classifies the event types of the activities."""
from pathlib import Path
from django.conf import settings
import pandas as pd

from extraction.logic.module import Module
from extraction.models import Prompt
from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u


class EventTypeClassifier(Module):
    """
    This module classifies the event types of the activities. The given event types are 'Symptom Onset',
    'Symptom Offset', 'Diagnosis', 'Doctor visit', 'Treatment', 'Hospital admission', 'Hospital discharge',
    'Medication', 'Lifestyle Change' and 'Feelings'. This is done so that we can extract a standardized set of event
    types from the Patient Journey. This is necessary for the application of process mining algorithms.
    """

    def __init__(self):
        super().__init__()
        self.name = "Event Type Classifier"
        self.description = "Classifies the event types for the corresponding activity labels from a Patient Journey."

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute(
        self,
        df: pd.DataFrame,
        patient_journey=None,
        patient_journey_sentences=None,
        cohort=None,
    ) -> pd.DataFrame:
        """Classifies corresponding event types for all activity labels in a dataframe."""
        super().execute(
            df,
            patient_journey=patient_journey,
            patient_journey_sentences=patient_journey_sentences,
            cohort=cohort,
        )

        df["event_type"] = df["activity"].apply(self.__classify_event_type)

        return df

    @staticmethod
    def __classify_event_type(activity_label):
        """Classify the event type for a given activity."""
        messages = Prompt.objects.get(name="EVENT_TYPE_MESSAGES").text
        messages.append({"role": "user", "content": activity_label})
        event_type = u.query_gpt(messages)

        return event_type
