from ..module import Module
from .. import utils as u
from .. import prompts as p

from pandas import DataFrame


class LocationExtractor(Module):
    def execute(self, _input, patient_journey=None):
        self.result = self.add_locations(_input)

    def add_locations(self, activity_labels):
        """Adds locations to the activity labels."""
        messages = [
            {"role": "system", "content": p.BULLETPOINTS_LOCATION_CONTEXT},
            {
                "role": "user",
                "content": p.BULLETPOINTS_LOCATION_PROMPT + activity_labels,
            },
            {"role": "assistant", "content": p.BULLETPOINTS_LOCATION_ANSWER},
        ]
        activity_labels_location = u.query_gpt(messages)
        activity_labels_location = self.remove_brackets(activity_labels_location)
        with open(
            (u.output_path / "intermediates/6_bulletpoints_with_location.txt"),
            "w",
        ) as f:
            f.write(activity_labels_location)
        return activity_labels_location

    @staticmethod
    def remove_brackets(activity_labels):
        """Removes brackets from within the activity_labels."""
        characters_to_remove = "()[]{}"
        for char in characters_to_remove:
            activity_labels = activity_labels.replace(char, "")
        return activity_labels
