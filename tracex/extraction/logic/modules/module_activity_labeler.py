from ..module import Module
from .. import utils as u
from .. import prompts as p

from pandas import DataFrame


class ActivityLabeler(Module):
    """
    This is the module that extracts the activity labels from the patient journey.
    """
    # Remove this, only for test purposes
    def __init__(self, name, description):
        super().__init__(name, description)
        print("ActivityLabeler module is ready")

    def execute(self, _input, patient_journey=None):
        super().execute(_input, patient_journey)
        self.result = self.extract_activities()

    # TODO: Convert to dataframes
    def extract_activities(self):
        """Converts the input text to activity_labels."""
        messages = [
            {"role": "system", "content": p.TXT_TO_BULLETPOINTS_CONTEXT},
            {
                "role": "user",
                "content": p.TXT_TO_BULLETPOINTS_PROMPT + self.patient_journey,
            },
            {"role": "assistant", "content": p.TXT_TO_BULLETPOINTS_ANSWER},
        ]
        activity_labels = u.query_gpt(messages)
        activity_labels = self._remove_commas(activity_labels)
        activity_labels = self._add_ending_commas(activity_labels)
        with open((u.output_path / "intermediates/1_bulletpoints.txt"), "w") as f:
            f.write(activity_labels)
        return activity_labels

    @staticmethod
    def _remove_commas(activity_labels):
        """Removes commas from within the activity_labels."""
        activity_labels = activity_labels.replace(", ", "/")
        activity_labels = activity_labels.replace(",", "/")
        return activity_labels

    @staticmethod
    def _add_ending_commas(activity_labels):
        """Adds commas at the end of each line."""
        activity_labels = activity_labels.replace("\n", ",\n")
        activity_labels = activity_labels + ","
        return activity_labels
