"""This is the module that extracts the time information from the patient journey."""
from datetime import datetime
from pathlib import Path

from ..logging import log_execution_time
from ..module import Module
from .. import prompts as p
from .. import utils as u


class TimeExtractor(Module):
    """
    This is the module that extracts the time information from the patient journey. This includes start dates,
    end dates and durations.
    """

    def __init__(self):
        super().__init__()
        self.name = "Time Extractor"
        self.description = "Extracts the timestamps for the corresponding activity labels from a patient journey."

    @log_execution_time(Path("extraction/logs/execution_time.log"))
    def execute(self, df, patient_journey=None):
        super().execute(df, patient_journey)
        df["start"] = df["activity"].apply(self.__extract_start)
        df["end"] = df.apply(self.__extract_end, axis=1)
        df["duration"] = df.apply(self.__calculate_row_duration, axis=1)
        return df

    def __extract_start(self, activity_label):
        """Extract the start date for a given activity."""
        messages = [
            {"role": "system", "content": p.START_CONTEXT},
            {
                "role": "user",
                "content": f"{p.START_PROMPT} \nThe text: {self.patient_journey} \n"
                f"The bulletpoint: {activity_label}",
            },
            {"role": "assistant", "content": p.START_ANSWER},
        ]
        output = u.query_gpt(messages)
        fc_message = [
            {"role": "system", "content": p.FC_START_CONTEXT},
            {"role": "user", "content": p.FC_START_PROMPT + "The text: " + output},
        ]
        start = u.query_gpt(
            fc_message,
            tool_choice={"type": "function", "function": {"name": "add_start"}},
        )

        return start

    def __extract_end(self, row):
        """Extract the end date for a given activity."""
        messages = [
            {"role": "system", "content": p.END_CONTEXT},
            {
                "role": "user",
                "content": f"{p.END_PROMPT} \nThe text: {self.patient_journey} \nThe bulletpoint: "
                f"{row['activity']} \nThe start date: {row['start']}",
            },
            {"role": "assistant", "content": p.END_ANSWER},
        ]
        output = u.query_gpt(messages)
        fc_message = [
            {"role": "system", "content": p.FC_END_CONTEXT},
            {"role": "user", "content": p.FC_END_PROMPT + "The text: " + output},
        ]
        end = u.query_gpt(
            fc_message,
            tool_choice={"type": "function", "function": {"name": "add_end"}},
        )

        return end

    @staticmethod
    def __calculate_row_duration(row):
        """Calculate the duration for a given activity."""
        if row["start"] == "N/A" or row["end"] == "N/A":
            return "N/A"
        start = datetime.strptime(row["start"], "%Y%m%dT%H%M")
        end = datetime.strptime(row["end"], "%Y%m%dT%H%M")
        duration = end - start
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
