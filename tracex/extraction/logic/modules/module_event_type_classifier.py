from ..module import Module
from .. import utils as u
from .. import prompts as p

from pandas import DataFrame


class EventTypeClassifier(Module):
    """
    This module classifies the event types of the activities. The given event types are 'Symptom Onset',
    'Symptom Offset', 'Diagnosis', 'Doctor visit', 'Treatment', 'Hospital admission', 'Hospital discharge',
    'Medication', 'Lifestyle Change' and 'Feelings'. This is done so that we can extract a standardized set of event
    types from the patient journey. This is necessary for the application of process mining algorithms.
    """

    def __init__(self):
        super().__init__()
        self.name = "Event Type Classifier"
        self.description = "Classifies the event types for the corresponding activity labels from a patient journey."

    def execute(self, _input, patient_journey=None):
        super().execute(_input, patient_journey)
        self.result = self.__add_event_types(_input)

    def __add_event_types(self, activity_labels):
        """Adds event types to the bulletpoints."""
        messages = [
            {"role": "system", "content": p.BULLETPOINTS_EVENT_TYPE_CONTEXT},
            {
                "role": "user",
                "content": p.BULLETPOINTS_EVENT_TYPE_PROMPT + activity_labels,
            },
            {"role": "assistant", "content": p.BULLETPOINTS_EVENT_TYPE_ANSWER},
        ]
        activity_labels_with_event_types = u.query_gpt(messages)
        activity_labels_with_event_types = self.__add_ending_commas(
            activity_labels_with_event_types
        )
        with open(
            (u.output_path / "intermediates/5_bulletpoints_with_event_type.txt"),
            "w",
        ) as f:
            f.write(activity_labels_with_event_types)
        return activity_labels_with_event_types

    # TODO: Remove when dataframes are used
    @staticmethod
    def __add_ending_commas(activity_labels):
        """Adds commas at the end of each line."""
        activity_labels = activity_labels.replace("\n", ",\n")
        activity_labels = activity_labels + ","
        return activity_labels
