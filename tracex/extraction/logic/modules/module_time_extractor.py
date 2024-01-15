from ..module import Module
from .. import utils as u
from .. import prompts as p

from pandas import DataFrame


class TimeExtractor(Module):
    """
    This is the module that extracts the time information from the patient journey. This includes start dates,
    end dates and durations.
    """
    def execute(self, _input, patient_journey=None):
        super().execute(_input, patient_journey)
        intermediate = self.add_start_dates(self.patient_journey, _input)
        intermediate = self.add_end_dates(self.patient_journey, intermediate)
        intermediate = self.add_durations(self.patient_journey, intermediate)
        self.result = intermediate

    def add_start_dates(self, patient_journey, activity_labels):
        """Adds start dates to the activity labels."""
        messages = [
            {"role": "system", "content": p.BULLETPOINTS_START_DATE_CONTEXT},
            {
                "role": "user",
                "content": p.BULLETPOINTS_START_DATE_PROMPT
                + patient_journey
                + "\n"
                + activity_labels,
            },
            {"role": "assistant", "content": p.BULLETPOINTS_START_DATE_ANSWER},
        ]
        activity_labels_start_dates = u.query_gpt(messages)
        activity_labels_start_dates = self._add_ending_commas(
            activity_labels_start_dates
        )
        with open(
            (u.output_path / "intermediates/2_bulletpoints_with_start.txt"),
            "w",
        ) as f:
            f.write(activity_labels_start_dates)
        return activity_labels_start_dates

    def add_end_dates(self, patient_journey, activity_labels):
        """Adds end dates to the bulletpoints."""
        messages = [
            {"role": "system", "content": p.BULLETPOINTS_END_DATE_CONTEXT},
            {
                "role": "user",
                "content": p.BULLETPOINTS_END_DATE_PROMPT
                + patient_journey
                + "\n"
                + activity_labels,
            },
            {"role": "assistant", "content": p.BULLETPOINTS_END_DATE_ANSWER},
        ]
        activity_labels_start_end_dates = u.query_gpt(messages)
        activity_labels_start_end_dates = self._add_ending_commas(
            activity_labels_start_end_dates
        )
        with open(
            (u.output_path / "intermediates/3_bulletpoints_with_end.txt"),
            "w",
        ) as f:
            f.write(activity_labels_start_end_dates)
        return activity_labels_start_end_dates

    def add_durations(self, patient_journey, activity_labels):
        """Adds durations to the bulletpoints."""
        messages = [
            {"role": "system", "content": p.BULLETPOINTS_DURATION_CONTEXT},
            {
                "role": "user",
                "content": p.BULLETPOINTS_DURATION_PROMPT
                + patient_journey
                + "\n"
                + activity_labels,
            },
            {"role": "assistant", "content": p.BULLETPOINTS_DURATION_ANSWER},
        ]
        activity_labels = u.query_gpt(messages)
        activity_labels = self._add_ending_commas(activity_labels)
        with open(
            (u.output_path / "intermediates/4_bulletpoints_with_duration.txt"),
            "w",
        ) as f:
            f.write(activity_labels)
        return activity_labels

    @staticmethod
    def _add_ending_commas(activity_labels):
        """Adds commas at the end of each line."""
        activity_labels = activity_labels.replace("\n", ",\n")
        activity_labels = activity_labels + ","
        return activity_labels
