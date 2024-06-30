"""Module providing classes for preprocessing patient input."""
from pathlib import Path
from django.conf import settings

from extraction.logic.module import Module
from extraction.models import Prompt
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
    ) -> str:
        """Preprocesses the patient input for better data quality."""
        super().execute(
            _input,
            patient_journey=patient_journey,
            patient_journey_sentences=patient_journey_sentences,
        )
        preprocessed_text = self.__apply_preprocessing_step(
            patient_journey, "SPELLCHECK"
        )
        print(preprocessed_text)
        print("TIME_IDENTIFICATION")
        preprocessed_text = self.__apply_preprocessing_step(
            preprocessed_text, "TIME_IDENTIFICATION"
        )
        print(preprocessed_text)
        print("TIME_Trans")
        preprocessed_text = self.__apply_preprocessing_step(
            preprocessed_text, "TRANS"
        )
        print(preprocessed_text)
        print("TIME_Interp")
        #preprocessed_text = self.__apply_preprocessing_step(
        #    preprocessed_text, "Interp"
        #)
        print(preprocessed_text)
        print("TIME_CALC")
        preprocessed_text = self.__apply_preprocessing_step(
            preprocessed_text, "CALC"
        )
        return preprocessed_text

    @staticmethod
    def __apply_preprocessing_step(text: str, prompt_name: str) -> str:
        """Applies a preprocessing step based on the step name."""
        messages = Prompt.objects.get(name=f"PREPROCESSING_{prompt_name}").text
        new_user_message = {"role": "user", "content": text}
        messages.append(new_user_message)
        preprocessed_text = u.query_gpt(messages)

        return preprocessed_text
