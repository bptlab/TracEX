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
    def execute(self, _input, patient_journey=None):
        """Extracts the activity labels from the patient journey."""
        super().execute(_input, patient_journey)

        return self.__extract_activities()

    def __extract_activities(self):
        """Converts the input text to activity_labels."""
        name = "activity"
        messages = [
            {"role": "system", "content": p.TXT_TO_ACTIVITY_CONTEXT},
            {
                "role": "user",
                "content": f"{p.TXT_TO_ACTIVITY_PROMPT} {self.patient_journey}",
            },
            {"role": "assistant", "content": p.TXT_TO_ACTIVITY_ANSWER},
        ]
        activity_labels = u.query_gpt(messages)
        # TODO: adjust prompt to remove "-" instead of replace()
        activity_labels = activity_labels.replace("- ", "").split("\n")
        df = pd.DataFrame(activity_labels, columns=[name])
        return df
