"""Module providing classes for preprocessing patient input."""
from pathlib import Path
from django.conf import settings

from extraction.logic.module import Module
from extraction.logic import prompts as p
from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u


class Preprocessor(Module):
    """
    This class provides functions for preprocessing the patient input
    to enhance data quality and interpretability.
    """

    def __init__(self):
        super().__init__()
        self.name = "Preprocessing Module"
        self.description = "Preprocesses patient input for better data quality."

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute(self, df=None, patient_journey=None):
        super().execute(df, patient_journey)
        preprocessed_text = self.spellcheck(patient_journey)
        preprocessed_text = self.punctuationcheck(preprocessed_text)
        preprocessed_text = self.identify_timestamps(preprocessed_text)
        preprocessed_text = self.transform_timestamps(preprocessed_text)
        preprocessed_text = self.interprete_timestamps(preprocessed_text)
        preprocessed_text = self.calculate_timestamps(preprocessed_text)

        return preprocessed_text

    def spellcheck(self, text):
        """Checks and corrects spelling and grammar in the input."""
        messages = p.PREPROCESSING_SPELLCHECK
        new_user_message = {"role": "user", "content": text}
        messages.append(new_user_message)
        preprocessed_text = u.query_gpt(messages)
        return preprocessed_text

    def punctuationcheck(self, text):
        """Checks and corrects punctuations and commas in the input."""
        messages = p.PREPROCESSING_PUNCTUATION
        new_user_message = {"role": "user", "content": text}
        messages.append(new_user_message)
        preprocessed_text = u.query_gpt(messages)
        return preprocessed_text

    def identify_timestamps(self, text):
        """Identifies and formats time specifications in the input."""
        messages = p.PREPROCESSING_IDENTIFY_TIMESTAMPS
        new_user_message = {"role": "user", "content": text}
        messages.append(new_user_message)
        preprocessed_text = u.query_gpt(messages)
        return preprocessed_text

    def transform_timestamps(self, text):
        """Adds a timeline to the input for better understanding of events."""
        messages = p.PREPROCESSING_TRANSFORM_TIMESTAMPS
        new_user_message = {"role": "user", "content": text}
        messages.append(new_user_message)
        preprocessed_text = u.query_gpt(messages)
        return preprocessed_text

    def calculate_timestamps(self, text):
        """Calculate a Timestamp to the input for better understanding of events."""
        messages = p.PREPROCESSING_TIME_CALCULATION
        new_user_message = {"role": "user", "content": text}
        messages.append(new_user_message)
        preprocessed_text = u.query_gpt(messages)
        return preprocessed_text

    def interprete_timestamps(self, text):
        """Interprete a Timestamp to the input for better understanding of events."""
        messages = p.PREPROCESSING_TIME_INTERPRETATION
        new_user_message = {"role": "user", "content": text}
        messages.append(new_user_message)
        preprocessed_text = u.query_gpt(messages)
        return preprocessed_text
