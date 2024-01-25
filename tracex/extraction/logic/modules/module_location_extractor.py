from pathlib import Path

from ..logging import log_execution_time
from ..module import Module
from .. import utils as u
from .. import prompts as p



class LocationExtractor(Module):
    """
    This is the module that extracts the location information from the patient journey to each activity.
    This means all activities are classified to the given locations "Home", "Hospital", "Doctors".
    """

    def __init__(self):
        super().__init__()
        self.name = "Location Extractor"
        self.description = "Extracts the locations for the corresponding activity labels from a patient journey."

    @log_execution_time(Path("extraction/logs/execution_time.log"))
    def execute(self, df, patient_journey=None):
        super().execute(df, patient_journey)
        self.result = self.__add_locations(df)

    def __add_locations(self, df):
        """Adds locations to the activity labels."""
        name = "attribute_location"
        df[name] = df["event_information"].apply(self.__classify_location)
        # document_intermediates(output)

        return df

    @staticmethod
    def __classify_location(activity_label):
        messages = [
            {"role": "system", "content": p.LOCATION_CONTEXT},
            {"role": "user", "content": f"{p.LOCATION_PROMPT} {activity_label}"},
            {"role": "assistant", "content": p.LOCATION_ANSWER},
        ]
        output = u.query_gpt(messages)

        fc_message = [
            {"role": "system", "content": p.FC_LOCATION_CONTEXT},
            {
                "role": "user",
                "content": f"{p.FC_LOCATION_PROMPT} The text: {output}",
            },
        ]
        location = u.query_gpt(
            messages=fc_message,
            tool_choice={"type": "function", "function": {"name": "add_location"}},
        )

        return location
