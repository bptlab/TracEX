"""This module extracts the time information from the patient journey."""
from datetime import datetime
from pathlib import Path
from django.conf import settings
import pandas as pd

from extraction.logic.module import Module
from extraction.logic import prompts as p
from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u


class TimeExtractor(Module):
    """
    This is the module that extracts the time information from the patient journey. This includes start dates,
    end dates and durations.
    """

    def __init__(self):
        super().__init__()
        self.name = "Time Extractor"
        self.description = "Extracts the timestamps for the corresponding activity labels from a patient journey."

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute(self, df, patient_journey=None, patient_journey_sentences=None):
        """This function extracts the time information from the patient journey."""
        super().execute(df, patient_journey, patient_journey_sentences)
        df["start"] = df.apply(self.__extract_start_date, axis=1)
        df["end"] = df.apply(self.__extract_end_date, axis=1)
        df = self.__post_processing(df)
        df["duration"] = df.apply(self.__calculate_duration, axis=1)

        return df

    def __extract_start_date(self, row):
        """Extract the start date for a given activity."""
        patient_journey_snippet = self.__get_snippet(row["sentence_id"])
        messages = p.START_DATE_MESSAGES[:]
        messages.append(
            {
                "role": "user",
                "content": "Text: "
                + patient_journey_snippet
                + "\nActivity label: "
                + row["activity"],
            }
        )
        start = u.query_gpt(messages)

        return start

    def __extract_end_date(self, row):
        """Extract the end date for a given activity."""
        patient_journey_snippet = self.__get_snippet(row["sentence_id"])
        messages = p.END_DATE_MESSAGES[:]
        messages.append(
            {
                "role": "user",
                "content": "\nText: "
                + patient_journey_snippet
                + "\nActivity label: "
                + row["activity"]
                + "\nStart date: "
                + row["start"],
            },
        )
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
        df["start"] = df["start"].ffill()  # Modified to avoid using inplace=True

        converted_end = pd.to_datetime(df["end"], format="%Y%m%dT%H%M", errors="coerce")
        mask = converted_end.isna()
        df.loc[mask, "end"] = converted_end
        df["end"] = df["end"].ffill()  # Modified to avoid using inplace=True

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

    def __get_snippet(self, sentence_id):
        """Extract the snippet for a given activity."""
        # We want to look at a snippet from the patient journey where we take five sentences into account
        # starting from the current sentence index -2 and ending at the current index +2
        # (writing +3 as python is exclusive on the upper bound)
        lower = max(0, int(sentence_id) - 2)
        upper = min(int(sentence_id) + 3, len(self.patient_journey_sentences))
        snippet = ". ".join(self.patient_journey_sentences[lower:upper])

        return snippet
