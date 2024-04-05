"""This module extracts the time information from the patient journey."""
from datetime import datetime
from pathlib import Path
from django.conf import settings

import pandas as pd

from extraction.logic.module import Module
from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u


class TimeExtractorBackup(Module):
    """
    This is the module that extracts the time information from the patient journey. This includes start dates,
    end dates and durations.
    """

    def __init__(self):
        super().__init__()
        self.name = "Time Extractor Backup"
        self.description = "Extracts the timestamps for the corresponding activity labels from a patient journey."

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute(self, df, patient_journey=None):
        super().execute(df, patient_journey)
        df["start"] = df["activity"].apply(self.__extract_start)
        df["end"] = df.apply(self.__extract_end_date, axis=1)
        df = self.__post_processing(df)
        df["duration"] = df.apply(self.__calculate_duration, axis=1)
        return df

    def __extract_start(self, activity_label):
        """Extract the start date for a given activity."""
        messages = [
            {"role": "system", "content": START_CONTEXT},
            {
                "role": "user",
                "content": f"The text: {self.patient_journey} \nThe activity label: {activity_label}",
            },
        ]
        start = u.query_gpt(messages)

        return start

    def __extract_end_date(self, row):
        """Extract the end date for a given activity."""
        messages = [
            {"role": "system", "content": END_CONTEXT},
            {
                "role": "user",
                "content": f"\nThe text: {self.patient_journey} \nThe activity label: "
                f"{row['activity']} \nThe start date: {row['start']}",
            },
        ]
        end = u.query_gpt(messages)

        return end

    @staticmethod
    def __calculate_duration(row):
        """Calculate the duration of an activity."""
        start = datetime.strptime(row["start"], "%Y%m%dT%H%M")
        end = datetime.strptime(row["end"], "%Y%m%dT%H%M")
        duration = end - start
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    @staticmethod
    def __post_processing(df):
        """Fill missing values for dates with default values."""

        def fix_end_dates(row):
            if row["end"] is pd.NaT and row["start"] is not pd.NaT:
                row["end"] = row["start"]

            return row

        converted_start = pd.to_datetime(
            df["start"], format="%Y%m%dT%H%M", errors="coerce"
        )
        mask = converted_start.isna()
        df.loc[mask, "start"] = converted_start
        df["start"].ffill(inplace=True)

        converted_end = pd.to_datetime(df["end"], format="%Y%m%dT%H%M", errors="coerce")
        mask = converted_end.isna()
        df.loc[mask, "end"] = converted_end
        df["end"].ffill(inplace=True)

        df = df.apply(fix_end_dates, axis=1)

        return df

    @staticmethod
    def is_valid_date_format(date_string, date_format):
        """Determine if a string matches the given date format."""
        try:
            datetime.strptime(date_string, date_format)

            return True
        except ValueError:

            return False


START_CONTEXT = """Extract the start date in the format YYYYMMDDT0000 for the corresponding activity label from
the patient journey. It is MANDATORY that you do the following: You may not return anything but a date in the format
YYYYMMDDT0000. For example, 20200101T0000. Do not return anything else. You are forbidden to return any other
information or sentence. If you have any doubt return "20200101T0000", but without the "" symbols."""


# """ You are provided with a natural language text containing various events. Your task is to identify the start
# date of a specific activity mentioned in the text. The activity label will be provided, and it is your job to
# extract only the start date associated with this activity from the text. Under no circumstances put anything else
# in the ouptut apart from the extracted start date. Please follow the following rules: 1. The format of the date
# should always be YYYYMMDDT0000. For example, 20200101T0000. 2. If only a month is mentioned then the date should
# always be the first day of the month. For example for March it should be 20200301T0000. 3. If the date is mentioned
# in a different format, please convert it to the format mentioned above. 4. Translate formulations like "the next
# day" or "over the following weeks" to the corresponding date. 5. Also consider context information from previous
# activities and their start dates. 6. If the start date is not mentioned output "N/A" instead. """

END_CONTEXT = """Extract the end date in the format YYYYMMDDT0000 for the corresponding activity label from the
patient journey. It is MANDATORY that you do the following: You may not return anything but a date in the format
YYYYMMDDT0000. For example, 20200101T0000. Do not return anything else. You are forbidden to return any other
information or sentence. If you have any doubt return "20200101T0000", but without the "" symbols."""

# """ You are provided with a natural language text containing various events. Your task is to identify the end date
# of a specific activity mentioned in the text. The activity label and the corresponding start date will be provided,
# and it is your job to extract only the end date associated with this activity from the text. Under no circumstances
# put anything else in the ouptut apart from the extracted end date. Please follow the following rules: 1. The format
# of the date should always be YYYYMMDDT0000. For example, 20200101T0000. 2. If only a month in mentioned then the
# date should always be the first day of the month. For example for March it should be 20200301T0000. 3. If the date
# is mentioned in a different format, please convert it to the format mentioned above. 4. Translate formulations like
# "the next day" or "over the following weeks" to the corresponding date. 5. Also consider context information from
# previous activities and their start dates and end dates. 6. End dates can not be earlier than the start dates. 7.
# If the end date is not mentioned output "N/A" instead. """
