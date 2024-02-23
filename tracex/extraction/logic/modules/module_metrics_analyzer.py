"""This module measures the outpupt of the pipeline based on specified metrics."""
from pathlib import Path
import pandas as pd
import numpy as np

from ..logging import log_execution_time
from ..module import Module
from .. import utils as u
from .. import prompts as p


class MetricsAnalyzer(Module):
    """
    This is the module that runs metrics on the pipelines output.
    The specified metrics currently used are:
    - relevance of event information
    - correctness of timestamps
    """

    def __init__(self):
        super().__init__()
        self.name = "Metrics Analyzer"
        self.description = (
            "Measures the output of the pipeline based on specified metrics."
        )

    @log_execution_time(Path("extraction/logs/execution_time.log"))
    def execute(self, df, patient_journey=None):
        super().execute(df, patient_journey)

        return self.__measure_metrics(df)

    def __measure_metrics(self, df):
        """Executing the measurement of metrics."""

        df["event_information_relevance"] = df["event_information"].apply(
            self.__rate_event_information_relevance
        )

        df[["timestamp_correctness", "correctness_confidence"]] = df.apply(
            lambda row: pd.Series(
                self.__rate_timestamps_correctness(
                    row["event_information"], row["start_date"], row["end_date"]
                )
            ),
            axis=1,
        )
        return df

    def __rate_event_information_relevance(self, event_information):
        category_mapping = {
            "No Relevance": 0,
            "Low Relevance": 1,
            "Moderate Relevance": 2,
            "High Relevance": 3,
        }

        messages = [
            {"role": "system", "content": p.METRIC_EVENT_INFORMATION_CONTEXT},
            {
                "role": "user",
                "content": f"{p.METRIC_EVENT_INFORMATION_PROMPT} \nThe bulletpoint: {event_information}\nThe patient journey: {self.patient_journey}",
            },
        ]

        answer = u.query_gpt(messages)
        for key in category_mapping.keys():
            if key in answer:
                category = key
                break

        return category

    def __rate_timestamps_correctness(self, event_information, start_date, end_date):
        messages = [
            {"role": "system", "content": p.METRIC_TIMESTAMPS_CONTEXT},
            {
                "role": "user",
                "content": f"{p.METRIC_TIMESTAMPS_PROMPT}\nThe bulletpoint: {event_information}\nThe start date related to the bulletpoint: {start_date}\nThe end date to the bulletpoint: {end_date}\nThe patient journey you should check the timestamps for the bulletpoint: {self.patient_journey}",
            },
        ]

        timestamp_correctness, top_logprops = u.query_gpt(
            messages, logprobs=True, top_logprobs=1
        )
        linear_prop = self.__calculate_linear_probability(top_logprops[0].logprob)
        return (timestamp_correctness, linear_prop)

    @staticmethod
    def __calculate_linear_probability(logprob):
        linear_prob = np.round(np.exp(logprob), 2)
        return linear_prob
