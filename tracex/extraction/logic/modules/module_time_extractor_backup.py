from datetime import datetime
from pathlib import Path

from ..logging import log_execution_time
from ..module import Module
from .. import prompts as p
from .. import utils as u


class TimeExtractorBackup(Module):
    """
    This is the module that extracts the time information from the patient journey. This includes start dates,
    end dates and durations.
    """

    def __init__(self):
        super().__init__()
        self.name = "Time Extractor Backup"
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
            {"role": "system", "content": START_DATE_CONTEXT},
            {
                "role": "user",
                "content": f"The text: {self.patient_journey} \nThe activity label: {activity_label}",
            },
        ]
        start_date = u.query_gpt(messages)
        print(start_date + "\n")
        assert (
            self.is_valid_date_format(start_date, "%Y%m%dT%H%M") is True
        ), f"Date {start_date} has no valid format."

        return start_date

    def __extract_end_date(self, row):
        messages = [
            {"role": "system", "content": END_DATE_CONTEXT},
            {
                "role": "user",
                "content": f"\nThe text: {self.patient_journey} \nThe activity label: "
                f"{row['event_information']} \nThe start date: {row['start']}",
            },
        ]
        end_date = u.query_gpt(messages)
        print(end_date + "\n")
        assert (
            self.is_valid_date_format(end_date, "%Y%m%dT%H%M") is True
        ), f"Date {end_date} has no valid format."

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

    @staticmethod
    def is_valid_date_format(date_string, date_format):
        try:
            datetime.strptime(date_string, date_format)
            return True
        except ValueError:
            return False


# START_DATE_CONTEXT = """
#     You are an expert in text understanding and your job is to take a given text and given summarizing bulletpoints and to add a start date to every bulletpoint.
#     Edit the bulletpoints in a way, that you just take the existing bulletpoints and add a start date at the end of it.
#     The information about the start date should be extracted from the text or from the context and should be as precise as possible.
#     Do not modify the content of the bulletpoint and keep ending commas.
#     Please use the format YYYYMMDD for the dates and extend every date by "T0000".
#     Keep in mind, that the start date of a bullet point is not necessarily later than the start of the previous one.
#     Also, the start date doesn't have to be the next date information in the text, but can be related to the previous.
#     If the text talks about getting medication and then improving and the bullet point says 'improving', you should return the date of getting the medication as start date.
#     If there is a conclusion at the end of the text and an outlook set the start date of the last bullet point to the start date of the corresponding bulletpoint.
#     If there is really no information about the start date to be extracted from the text but there is information about events happening at the same time,
#     use that information to draw conclusions about the start dates.
#     If there is no information about the start date at all and there is no way of finding some, delete that bulletpoint.
#     The only output should be the updated bullet points, nothing else!
# """

START_DATE_CONTEXT = """
    You are provided with a natural language text containing various events. Your task is to identify the start date of
    a specific activity mentioned in the text. The activity label will be provided, and it is your job to extract only
    the start date associated with this activity from the text.
    Under no circumstances put anything else in the ouptut apart from the extracted start date.
    Please follow the following rules:
    1. The format of the date should always be YYYYMMDDT0000. For example, 20200101T0000.
    2. If only a month is mentioned then the date should always be the first day of the month. For example for March it should be 20200301T0000.
    3. If the date is mentioned in a different format, please convert it to the format mentioned above.
    4. Translate formulations like "the next day" or "over the following weeks" to the corresponding date.
    5. Also consider context information from previous activities and their start dates.
"""

# END_DATE_CONTEXT = """
#     You are an expert in text understanding and your job is to take a given text and given summarizing bulletpoints with a start date and to add a end date to every bulletpoint.
#     It is important, that every bullet point gets an end date, even if it is the same as the start date.
#     Edit the bulletpoints in a way, that you just take the existing bulletpoints and add a end date to it.
#     The information about the end date should be extracted from the text or from the context and should be as precise as possible.
#     Please use the format YYYYMMDD for the dates and extend every date by "T0000".
#     If the duration of an event is given, use that information to draw conclusions about the end date.
#     If the duration of an event is not given, use the context to draw conclusions about the end date.
#     If two bulletpoints are related, it is possible, that the end dates should match.
#     Think about how long humans tend to stay in hospitals, how long it takes to recover from a disease, how long they practice new habits and so on.
#     If there is no information about the end date at all, please state the start date also as the end date.
#     The only output should be the updated bullet points, nothing else!
# """

END_DATE_CONTEXT = """
    You are provided with a natural language text containing various events. Your task is to identify the end date of
    a specific activity mentioned in the text. The activity label and the corresponding start date will be provided,
    and it is your job to extract only the end date associated with this activity from the text.
    Under no circumstances put anything else in the ouptut apart from the extracted end date.
    Please follow the following rules:
    1. The format of the date should always be YYYYMMDDT0000. For example, 20200101T0000.
    2. If only a month in mentioned then the date should always be the first day of the month. For example for March it should be 20200301T0000.
    3. If the date is mentioned in a different format, please convert it to the format mentioned above.
    4. Translate formulations like "the next day" or "over the following weeks" to the corresponding date.
    5. Also consider context information from previous activities and their start dates and end dates.
    6. End dates can not be earlier than the start dates.
"""
