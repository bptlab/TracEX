"""This is the module that extracts the activity labels from the patient journey."""
from pathlib import Path
import pandas as pd
from django.conf import settings

from extraction.logic.module import Module
from extraction.models import Prompt
from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u


class ActivityLabeler(Module):
    """
    This is the module that extracts the activity labels from the patient journey.
    """

    def __init__(self):
        super().__init__()
        self.name = "Activity Labeler"
        self.description = "Extracts the activity labels from a patient journey."

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute(
        self,
        _input=None,
        patient_journey=None,
        patient_journey_sentences=None,
        cohort=None,
    ):
        """
        Extracts the activity labels from the patient journey with the following steps:
        1. Number the patient journey sentences to enable selecting a specific range of sentences.
        2. Extract the activity labels from the patient journey using chatgpt.
        """
        super().execute(
            _input,
            patient_journey=patient_journey,
            patient_journey_sentences=patient_journey_sentences,
            cohort=cohort,
        )

        condition = cohort["condition"] if cohort is not None else None

        patient_journey_numbered = self.__number_patient_journey_sentences(
            patient_journey_sentences
        )
        activity_labels = self.__extract_activities(patient_journey_numbered, condition)
        new_activity_labels = self.__extract_new_activities(
            patient_journey_numbered, condition
        )
        print(pd.concat([activity_labels, new_activity_labels], axis="columns"))

        return activity_labels

    @staticmethod
    def __number_patient_journey_sentences(patient_journey_sentences):
        """
        Number the patient journey sentences in the format:
            1: ...
            2: ...
        And so on.
        """
        patient_journey_numbered = patient_journey_sentences[:]
        for count, value in enumerate(patient_journey_numbered):
            patient_journey_numbered[count] = f"{count}: {value}"
        patient_journey_numbered = "\n".join(patient_journey_numbered)

        return patient_journey_numbered

    @staticmethod
    def __extract_activities(patient_journey_numbered, condition):
        """
        Converts a patient journey, where every sentence is numbered, to a DataFrame with the activity labels by
        extracting the activity labels from the patient journey.
        """
        column_name = "activity"
        messages = Prompt.objects.get(name="TEXT_TO_ACTIVITY_MESSAGES").text
        # if condition is not None:
        #     messages.append(
        #         {
        #             "role": "user",
        #             "content": "Consider all important points regarding the course of the disease of "
        #             + condition,
        #         }
        #     )
        messages.append({"role": "user", "content": patient_journey_numbered})
        activity_labels = u.query_gpt(messages).split("\n")
        df = pd.DataFrame(activity_labels, columns=[column_name])
        df[["activity", "sentence_id"]] = df["activity"].str.split(" #", expand=True)

        return df

    @staticmethod
    def __extract_new_activities(patient_journey_numbered, condition):
        """
        Converts a patient journey, where every sentence is numbered, to a DataFrame with the activity labels by
        extracting the activity labels from the patient journey.
        """
        column_name = "activity"
        messages = [
            {
                "role": "system",
                "content": "You are an expert in text understanding and summarization. Your Job is to take a given text about Covid-19 and convert it into bullet points. Think step by step: First think about which events are typically present in a Covid-19 Course of disease. Then scan the text and determine which of the events you find are relevant to Covid-19. Finally, summarize only the relevant events in bullet points. Do not include time dates and use a maximum of 6 words per bullet point. Include the number of the sentence in the text from which you take the bullet point. The related numbers are in front of the sentences. ",
            },
            {
                "role": "user",
                "content": "1: On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, "
                "fatigue, and a low-grade fever.\n2: Four days later I went to the doctor and got tested "
                "positive for Covid19.\n3: Then I got hospitalized for two weeks.",
            },
            {
                "role": "assistant",
                "content": "starting to experience symptoms #1\nvisiting doctor's #2\ntesting positive for Covid19 "
                "#2\ngetting admissioned to hospital #3\ngetting discharged from hospital #3",
            },
            {
                "role": "user",
                "content": "8: Concerned about my condition, I contacted my primary care physician via phone.\n9: He "
                "advised me to monitor my symptoms and stay at home unless they became severe.",
            },
            {
                "role": "assistant",
                "content": "contacting primary care physician #8\nmonitoring symptoms at home #9",
            },
            {"role": "user", "content": "5: First symptoms on 01/04/2020"},
            {"role": "assistant", "content": "starting to experience symptoms #5"},
            {
                "role": "user",
                "content": "1: On July 15, 2022, I started experiencing the first symptoms of Covid-19 for five "
                "days.\n2: Initially, I had a mild cough and fatigue.",
            },
            {
                "role": "assistant",
                "content": "starting to experience symptoms #1\nending to experience symptoms #1",
            },
            {
                "role": "user",
                "content": "5:After surviving Covid-19, I made getting vaccinated a top priority. 6: I received my first "
                "dose of the vaccine in early February 2022 and the second dose three weeks later. 7: Despite "
                "the challenges I faced during my infection, I remained determined to protect myself and "
                "others from the virus by getting vaccinated.",
            },
            {
                "role": "assistant",
                "content": "receiving fist dose of vaccine #6\nreceiving second dose of vaccine #6",
            },
            {"role": "user", "content": f"{patient_journey_numbered}"},
        ]
        activity_labels = u.query_gpt(messages).split("\n")

        df = pd.DataFrame(activity_labels, columns=[column_name])
        df[["activity", "sentence_id"]] = df["activity"].str.split(" #", expand=True)

        return df
