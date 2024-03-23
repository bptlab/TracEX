"""This module compares an event log created by the pipeline against a manually created ground truth."""
from pathlib import Path
import pandas as pd
from django.conf import settings

from tracex.tracex.logic.logger import log_execution_time
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
    def execute(self, df, patient_journey=None):
        super().execute(df, patient_journey)

        return self.__compare_event_logs(df)

    def __compare_event_logs(self, df):
        """Comparing the event logs."""
        # Check if the comparison patient journey is the same as the one used in the pipeline not yet implemented
        ground_truth_df = pd.read_csv(
            c.comparison_path / "journey_test_1_comparison_basis.csv"
        )

        return self.__start_comparison(df, ground_truth_df)

    def __start_comparison(self, pipeline_df, ground_truth_df):
        matching_perc_pipeline_to_ground_truth = self.__compare_activities(
            pipeline_df, ground_truth_df
        )

        matching_perc_ground_truth_to_pipeline = self.__compare_activities(
            ground_truth_df, pipeline_df
        )

        with open(c.output_path.joinpath("event_log_comparison.txt"), "w") as f:
            f.write(
                "Percentage of event information found by the pipeline that are contained in ground truth: "
                + str(matching_perc_pipeline_to_ground_truth)
                + "\n"
            )
            f.write(
                "Percentage of event information in the ground truth that are contained event log by the pipeline: "
                + str(matching_perc_ground_truth_to_pipeline)
                + "\n"
            )

        return pipeline_df

    def __compare_activities(self, input_df, comparison_basis_df):
        total_matching_activities = 0
        for activity in input_df["activity"]:
            total_matching_activities += self.__find_activity(
                activity, comparison_basis_df
            )
        matching_percentage = round(total_matching_activities / input_df.shape[0], 2)
        return matching_percentage

    @staticmethod
    def __find_activity(activity, comparison_basis_df):
        for comparison_activity in comparison_basis_df["activity"]:
            messages = [
                {"role": "system", "content": p.COMPARE_CONTEXT},
                {
                    "role": "user",
                    "content": f"{p.COMPARE_PROMPT} + {activity}\n {comparison_activity}",
                },
            ]
            response = u.query_gpt(messages)
            with open(c.output_path.joinpath("compare.txt"), "a") as f:
                f.write(
                    activity
                    + " comparing with: "
                    + comparison_activity
                    + ":\n\n"
                    + response
                    + "\n\n\n"
                )
            if "True" in response:
                return 1
        return 0
