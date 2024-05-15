"""This module extracts the time information from the patient journey."""
from pathlib import Path
from django.conf import settings
import pandas as pd

from extraction.logic.module import Module
from extraction.models import Prompt
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
        super().execute(
            df,
            patient_journey=patient_journey,
            patient_journey_sentences=patient_journey_sentences,
        )

        df["time:timestamp"] = df.apply(self.__extract_start_date, axis=1)
        df["time:end_timestamp"] = df.apply(self.__extract_end_date, axis=1)
        df = self.__post_processing(df)
        df["time:duration"] = df.apply(self.__calculate_duration, axis=1)

        return df

    def __extract_start_date(self, row):
        """Extract the start date for a given activity."""
        lower, upper = u.get_snippet_bounds(
            index=(int(row["sentence_id"])), length=len(self.patient_journey_sentences)
        )
        patient_journey_snippet = ". ".join(self.patient_journey_sentences[lower:upper])
        messages = Prompt.objects.get(name="START_DATE_MESSAGES").text
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
        lower, upper = u.get_snippet_bounds(
            index=(int(row["sentence_id"])), length=len(self.patient_journey_sentences)
        )
        patient_journey_snippet = ". ".join(self.patient_journey_sentences[lower:upper])
        messages = Prompt.objects.get(name="END_DATE_MESSAGES").text
        messages.append(
            {
                "role": "user",
                "content": "\nText: "
                + patient_journey_snippet
                + "\nActivity label: "
                + row["activity"]
                + "\nStart date: "
                + row["time:timestamp"],
            },
        )
        end = u.query_gpt(messages)

        return end

    @staticmethod
    def __calculate_duration(row):
        """Calculate the duration of an activity."""
        duration = row["time:end_timestamp"] - row["time:timestamp"]
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    @staticmethod
    def __post_processing(df):
        """Fill missing values for dates with default values."""

        def fix_end_dates(row):
            if (
                row["time:end_timestamp"] is pd.NaT
                and row["time:timestamp"] is not pd.NaT
            ):
                row["time:end_timestamp"] = row["time:timestamp"]

            return row

        df["time:timestamp"] = pd.to_datetime(
            df["time:timestamp"], format="%Y%m%dT%H%M", errors="coerce"
        )
        df["time:end_timestamp"] = pd.to_datetime(
            df["time:end_timestamp"], format="%Y%m%dT%H%M", errors="coerce"
        )

        if df["time:timestamp"].isna().all():
            df["time:timestamp"] = df["time:timestamp"].fillna(
                pd.Timestamp("2020-01-01 00:00")
            )

        if df["time:end_timestamp"].isna().all():
            df["time:end_timestamp"] = df["time:end_timestamp"].fillna(
                pd.Timestamp("2020-01-01 00:00")
            )

        df["time:timestamp"] = df["time:timestamp"].ffill().bfill()
        df["time:end_timestamp"] = df["time:end_timestamp"].ffill().bfill()

        df = df.apply(fix_end_dates, axis=1)

        return df
