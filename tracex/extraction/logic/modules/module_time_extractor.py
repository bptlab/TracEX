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
        df["start"] = df["event_information"].apply(self.__extract_start_date)
        df["end"] = df.apply(self.__extract_end_date, axis=1)
        df["duration"] = df.apply(self.__calculate_row_duration, axis=1)
        self.result = df

    def __extract_start_date(self, activity_label):
        messages = [
            {"role": "system", "content": p.START_DATE_CONTEXT},
            {
                "role": "user",
                "content": f"{p.START_DATE_PROMPT} \nThe text: {self.patient_journey} \nThe bulletpoint: {activity_label}",
            },
            {"role": "assistant", "content": p.START_DATE_ANSWER},
        ]
        output = u.query_gpt(messages)
        print(output + "\n")
        fc_message = [
            {"role": "system", "content": p.FC_START_DATE_CONTEXT},
            {"role": "user", "content": p.FC_START_DATE_PROMPT + "The text: " + output},
        ]
        start_date = u.query_gpt(
            fc_message,
            tool_choice={"type": "function", "function": {"name": "add_start_dates"}},
        )

        return start_date

    def __extract_end_date(self, row):
        messages = [
            {"role": "system", "content": p.END_DATE_CONTEXT},
            {
                "role": "user",
                "content": f"{p.END_DATE_PROMPT} \nThe text: {self.patient_journey} \nThe bulletpoint: "
                           f"{row['event_information']} \nThe start date: {row['start']}",
            },
            {"role": "assistant", "content": p.END_DATE_ANSWER},
        ]
        output = u.query_gpt(messages)
        fc_message = [
            {"role": "system", "content": p.FC_END_DATE_CONTEXT},
            {"role": "user", "content": p.FC_END_DATE_PROMPT + "The text: " + output},
        ]
        end_date = u.query_gpt(
            fc_message,
            tool_choice={"type": "function", "function": {"name": "add_end_dates"}},
        )

        return end_date

    @staticmethod
    def __calculate_row_duration(row):
        if row["start"] == "N/A" or row["end"] == "N/A":
            return "N/A"
        start_date = datetime.strptime(row["start"], "%Y%m%dT%H%M")
        end_date = datetime.strptime(row["end"], "%Y%m%dT%H%M")
        duration = end_date - start_date
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
