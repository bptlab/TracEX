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
        self.name = "Preprocessor"
        self.description = "Preprocesses patient input for better data quality."

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute(
        self, _input=None, patient_journey=None, patient_journey_sentences=None
    ):
        """Preprocesses the patient input for better data quality."""
        super().execute(_input, patient_journey=patient_journey, patient_journey_sentences=patient_journey_sentences)
        preprocessed_text = self.__spellcheck(patient_journey)
        preprocessed_text = self.__punctuationcheck(preprocessed_text)
        preprocessed_text = self.__identify_timestamps(preprocessed_text)
        preprocessed_text = self.__transform_timestamps(preprocessed_text)
        preprocessed_text = self.__interpret_timestamps(preprocessed_text)
        preprocessed_text = self.__calculate_timestamps(preprocessed_text)
        patient_journey_sentences = self.__make_sentences(preprocessed_text)

        return patient_journey_sentences

    @staticmethod
    def __make_sentences(text):
        """Splits the input into a list of its sentences."""
        text = text.replace("\n", " ")
        text = text.split(". ")

        return text

    @staticmethod
    def __spellcheck(text):
        """Checks and corrects spelling and grammar in the input."""
        messages = p.PREPROCESSING_SPELLCHECK
        new_user_message = {"role": "user", "content": text}
        messages.append(new_user_message)
        preprocessed_text = u.query_gpt(messages)

        return preprocessed_text

    @staticmethod
    def __punctuationcheck(text):
        """Checks and corrects punctuations and commas in the input."""
        messages = p.PREPROCESSING_PUNCTUATION
        new_user_message = {"role": "user", "content": text}
        messages.append(new_user_message)
        preprocessed_text = u.query_gpt(messages)

        return preprocessed_text

    @staticmethod
    def __identify_timestamps(text):
        """Identifies and formats time specifications in the input."""
        messages = p.PREPROCESSING_IDENTIFY_TIMESTAMPS
        new_user_message = {"role": "user", "content": text}
        messages.append(new_user_message)
        preprocessed_text = u.query_gpt(messages)

        return preprocessed_text

    @staticmethod
    def __transform_timestamps(text):
        """Adds a timeline to the input for better understanding of events."""
        messages = p.PREPROCESSING_TRANSFORM_TIMESTAMPS
        new_user_message = {"role": "user", "content": text}
        messages.append(new_user_message)
        preprocessed_text = u.query_gpt(messages)

        return preprocessed_text

    @staticmethod
    def __calculate_timestamps(text):
        """Calculate a Timestamp to the input for better understanding of events."""
        messages = p.PREPROCESSING_TIME_CALCULATION
        new_user_message = {"role": "user", "content": text}
        messages.append(new_user_message)
        preprocessed_text = u.query_gpt(messages)

        return preprocessed_text

    @staticmethod
    def __interpret_timestamps(text):
        """Interpret a Timestamp to the input for better understanding of events."""
        messages = p.PREPROCESSING_TIME_INTERPRETATION
        new_user_message = {"role": "user", "content": text}
        messages.append(new_user_message)
        preprocessed_text = u.query_gpt(messages)

        return preprocessed_text
