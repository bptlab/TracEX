"""This is the module that extracts the activity labels from the patient journey."""
from pathlib import Path
import pandas as pd
from django.conf import settings

from ..logging import log_execution_time
from ..module import Module
from .. import prompts as p
from .. import utils as u


class ActivityLabeler(Module):
    """
    This is the module that extracts the activity labels from the patient journey.
    """

    def __init__(self):
        super().__init__()
        self.name = "Activity Labeler"
        self.description = "Extracts the activity labels from a patient journey."

    @log_execution_time(Path(settings.BASE_DIR / "extraction/logs/execution_time.log"))
    def execute(self, _input, patient_journey=None):
        super().execute(_input, patient_journey)

        return self.__extract_activities()

    def __extract_activities(self):
        """Converts the input text to activity_labels."""
        patient_journey = self.patient_journey
        for i in range(len(patient_journey)):
            patient_journey[i] = str(i) + ": " + patient_journey[i]
        patient_journey = ".\n".join(patient_journey)
                
        name = "activity"
        messages = p.TEXT_TO_ACTIVITY_MESSAGES[:]
        messages.append({"role": "user", "content": patient_journey})
        activity_labels = u.query_gpt(messages)
        activity_labels = activity_labels.split("\n")
        df = pd.DataFrame(activity_labels, columns=[name])
        df[["activity", "sentence_id"]] = df["activity"].str.split(" #", expand=True)
        
        df.to_csv(u.output_path / "activity_labels.csv", index=False)
        
        return df