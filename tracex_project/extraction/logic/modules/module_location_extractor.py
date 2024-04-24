"""This module that extracts the location information for each activity."""
from pathlib import Path
from django.conf import settings

from extraction.logic.module import Module
from extraction.logic import prompts as p
from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u


class LocationExtractor(Module):
    """
    This is the module that extracts the location information from the patient journey to each activity.
    This means all activities are classified to the given locations "Home", "Hospital", "Doctors".
    """

    def __init__(self):
        super().__init__()
        self.name = "Location Extractor"
        self.description = "Extracts the locations for the corresponding activity labels from a patient journey."

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute(self, df, patient_journey=None, patient_journey_sentences=None):
        """Extracts the location information for each activity."""
        super().execute(df, patient_journey=patient_journey, patient_journey_sentences=patient_journey_sentences)

        column_name = "attribute_location"
        df[column_name] = df["activity"].apply(self.__classify_location)

        return df

    @staticmethod
    def __classify_location(activity_label):
        """Classify the location for a given activity."""
        messages = p.LOCATION_MESSAGES[:]
        messages.append({"role": "user", "content": activity_label})
        location = u.query_gpt(messages)

        return location
