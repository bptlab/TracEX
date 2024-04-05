"""This module compares an event log created by the pipeline against a manually created ground truth."""
import time
from pathlib import Path
import pandas as pd
from django.conf import settings

from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u
from tracex.logic import constants as c
from ..module import Module
from .. import prompts as p


class EventLogComparator(Module):
    """
    This is the module that compares the event log created by the pipeline
    against a manually created ground truth. We provide three different event
    logs with the according patient journey as a ground truth in
    tracex/extraction/content/comparison.
    """

    def __init__(self):
        super().__init__()
        self.name = "Event Log Comparator"
        self.description = "Compares the output of the pipeline against a ground truth."

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute(self, df, patient_journey=None, patient_journey_sentences=None):
        super().execute(df, patient_journey, patient_journey_sentences)

        return self.__compare_event_logs(df)

    def __compare_event_logs(self, df):
        """Comparing the event logs."""
        # Check if the comparison patient journey is the same as the one used in the pipeline not yet implemented
        ground_truth_df = pd.read_csv(
            c.comparison_path / "journey_test_1_comparison_basis.csv"
        )

        return self.__start_comparison(df, ground_truth_df)

    def __start_comparison(self, pipeline_df, ground_truth_df):
        with open(c.output_path.joinpath("compare.txt"), "w") as f:
            f.write("\n")

        matching_perc_pipeline_to_ground_truth = self.__compare_activities(
            pipeline_df, ground_truth_df
        )

        matching_perc_ground_truth_to_pipeline = self.__compare_activities(
            ground_truth_df, pipeline_df
        )

        with open(c.output_path.joinpath("event_log_comparison.txt"), "w") as f:
            f.write(
                "Percentage of activities found by the pipeline that are contained in ground truth: "
                + str(matching_perc_pipeline_to_ground_truth)
                + "%\n\n"
            )
            f.write(
                "Percentage of activities contained in ground truth that are found by the pipeline: "
                + str(matching_perc_ground_truth_to_pipeline)
                + "%\n"
            )

        return pipeline_df

    def __compare_activities(self, input_df, comparison_basis_df):
        total_matching_activities = 0
        for index, activity in enumerate(input_df["activity"]):
            total_matching_activities += self.__find_activity(
                activity, comparison_basis_df, index
            )
            time.sleep(2)
        matching_percentage = round(total_matching_activities / input_df.shape[0], 2)
        matching_percentage = round(matching_percentage * 100, 0)

        return matching_percentage

    @staticmethod
    def __find_activity(activity, comparison_basis_df, index):
        # We want to look at a snippet from the other dataframe where we take five activities into account
        # starting from the current index -2 and ending at the current index +2 (writing +3 as python is exclusive on the upper bound)
        lower = max(0, index - 2)
        upper = min(len(comparison_basis_df), index + 3)
        for comparison_activity in comparison_basis_df["activity"][lower:upper]:
            messages = p.COMPARE_MESSAGES[:]
            messages.append(
                {
                    "role": "user",
                    "content": f"First: {activity}\nSecond: {comparison_activity}",
                }
            )
            response = u.query_gpt(messages)

            if "True" in response:
                return 1
        return 0
