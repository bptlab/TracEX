"""This module measures the outpupt of the pipeline based on specified metrics."""
from pathlib import Path
import pandas as pd
from django.conf import settings

from extraction.logic.module import Module
from extraction.models import Prompt
from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u


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

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute(self, df, patient_journey=None, patient_journey_sentences=None):
        """Executing the measurement of metrics. The metrics output will be written on disk as a csv file.
        The dataframe without the metrics is returned for visualization."""
        super().execute(
            df,
            patient_journey=patient_journey,
            patient_journey_sentences=patient_journey_sentences,
        )

        metrics_df = df.copy()
        metrics_df["activity_relevance"] = metrics_df["activity"].apply(
            self.__rate_activity_relevance
        )
        metrics_df[
            ["timestamp_correctness", "correctness_confidence"]
        ] = metrics_df.apply(
            lambda row: pd.Series(
                self.__rate_timestamps_correctness(
                    row["activity"], row["time:timestamp"], row["time:end_timestamp"]
                )
            ),
            axis=1,
        )

        return metrics_df

    @staticmethod
    def __rate_activity_relevance(activity):
        category_mapping = {
            "No Relevance": 0,
            "Low Relevance": 1,
            "Moderate Relevance": 2,
            "High Relevance": 3,
        }

        messages = Prompt.objects.get(name="METRIC_ACTIVITY_MESSAGES").text
        messages.append({"role": "user", "content": activity})

        response = u.query_gpt(messages)
        category = "No Relevance"  # By default, an activity is not relevant.
        for key in category_mapping:
            if key in response:
                category = key
                break

        return category

    def __rate_timestamps_correctness(self, activity, start, end):
        messages = Prompt.objects.get(name="METRIC_TIMESTAMP_MESSAGES").text
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
        linear_prop = u.calculate_linear_probability(top_logprops[0].logprob)

        return timestamp_correctness, linear_prop
