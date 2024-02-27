"""This module compares an event log created by the pipeline against a manual created ground truth."""
from pathlib import Path
import pandas as pd

from ..logging import log_execution_time
from ..module import Module
from .. import prompts as p
from .. import utils as u
from .. import constants as c


class EventLogComparator(Module):
    """
    This is the module that compares the event log created by the pipeline against a manual created ground truth.
    We provide three different event logs with the according patient journey as a ground truth in tracex/extraction/content/comparison.
    """

    def __init__(self):
        super().__init__()
        self.name = "Event Log Comparator"
        self.description = "Compares the output of the pipeline against a ground truth."

    @log_execution_time(Path("extraction/logs/execution_time.log"))
    def execute(self, df, patient_journey=None):
        super().execute(df, patient_journey)

        return self.__compare_event_logs(df)

    def __compare_event_logs(self, df):
        """Comparing the event logs."""
        ground_truth_df = pd.read_csv(
            c.comparison_path / "journey_test_1_comparison_basis.csv"
        )

        return self.__start_comparison(df, ground_truth_df)

    def __start_comparison(self, pipeline_df, ground_truth_df):
        matching_perc_pipeline_to_ground_truth = self.__compare_given_to_manual(
            pipeline_df, ground_truth_df
        )
        print(
            "Percentage of event information found by the pipeline that are contained in ground truth: "
            + str(matching_perc_pipeline_to_ground_truth)
        )
        matching_perc_ground_truth_to_pipeline = self.__compare_manual_to_given(
            ground_truth_df, pipeline_df
        )
        print(
            "Percentage of event information in the ground truth that are contained event log by the pipeline: "
            + str(matching_perc_ground_truth_to_pipeline)
        )
        return None

    def __compare_given_to_manual(self, pipeline_df, ground_truth_df):
        total_matching_activities = 0
        for activity in pipeline_df["activity"]:
            total_matching_activities += self.__find_activity(
                activity, ground_truth_df
            )
        matching_percentage = round(
            total_matching_activities / pipeline_df.shape[0], 2
        )
        return matching_percentage

    def __compare_manual_to_given(self, ground_truth_df, pipeline_df):
        total_matching_activities = 0
        for activity in ground_truth_df["activity"]:
            total_matching_activities += self.__find_activity(
                activity, pipeline_df
            )
        matching_percentage = round(
            total_matching_activities / pipeline_df.shape[0], 2
        )
        return matching_percentage

    @staticmethod
    def __find_activity(activity, ground_truth_df):
        for row in ground_truth_df["activity"]:
            message = [
                {"role": "system", "content": p.COMPARE_CONTEXT},
                {
                    "role": "user",
                    "content": f"{p.COMPARE_PROMPT} + given_activity\n {row}",
                },
            ]
            response = u.query_gpt(messages=message)
            with open(u.output_path / "compare.txt", "a") as f:
                f.write(
                    activity
                    + " comparing with: "
                    + row
                    + ":\n\n"
                    + response
                    + "\n\n\n"
                )
            if "True" in response:
                return 1
        return 0
