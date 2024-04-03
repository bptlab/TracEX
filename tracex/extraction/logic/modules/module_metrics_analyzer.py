"""This module measures the outpupt of the pipeline based on specified metrics."""
from pathlib import Path
import pandas as pd
import numpy as np
from django.conf import settings

from ..logging import log_execution_time
from ..module import Module
from .. import utils as u
from .. import prompts as p
from .. import constants as c


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

    @log_execution_time(Path(settings.BASE_DIR / "extraction/logs/execution_time.log"))
    def execute(self, df, patient_journey=None):
        super().execute(df, patient_journey)

        return self.__measure_metrics(df)

    def __measure_metrics(self, df):
        """Executing the measurement of metrics. The metrics output will be written on disk as a csv file.
        The dataframe without the metrics is returned for visualization."""

        metrics_df = df.copy()
        metrics_df["activity_relevance"] = metrics_df["activity"].apply(
            self.__rate_activity_relevance
        )

        metrics_df[
            ["timestamp_correctness", "correctness_confidence"]
        ] = metrics_df.apply(
            lambda row: pd.Series(
                self.__rate_timestamps_correctness(
                    row["activity"], row["start"], row["end"]
                )
            ),
            axis=1,
        )

        metrics_df.to_csv(
            Path(c.output_path.joinpath("metrics.csv")), index=False, sep=","
        )

        return df

    def __rate_activity_relevance(self, activity):
        category_mapping = {
            "No Relevance": 0,
            "Low Relevance": 1,
            "Moderate Relevance": 2,
            "High Relevance": 3,
        }

        messages = p.METRIC_ACTIVITY_MESSAGES[:]
        messages.append({"role": "user", "content": activity})

        response = u.query_gpt(messages)
        for key in category_mapping:
            if key in response:
                category = key
                break

        return category

    def __rate_timestamps_correctness(self, activity, start, end):
        messages = p.METRIC_TIMESTAMP_MESSAGES[:]
        messages.append(
            {
                "role": "user",
                "content": (
                    f"Text: {self.patient_journey}\nActivity: {activity}\n\
                Start date: {start}\nEnd date: {end}\n"
                ),
            }
        )

        timestamp_correctness, top_logprops = u.query_gpt(
            messages, logprobs=True, top_logprobs=1
        )
        linear_prop = self.__calculate_linear_probability(top_logprops[0].logprob)
        return (timestamp_correctness, linear_prop)

    @staticmethod
    def __calculate_linear_probability(logprob):
        linear_prob = np.round(np.exp(logprob), 2)
        return linear_prob
