""""The event log comparator compares the event log created by the pipeline against a manually created ground truth."""
import time
from pathlib import Path
from django.conf import settings

from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u
from tracex.logic import constants as c
from . import prompts as p


@log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
def comparing_event_logs(pipeline_df, ground_truth_df):
    """Comparing event logs."""
    with open(c.output_path.joinpath("compare.txt"), "w") as f:
        f.write("\n")

    matching_perc_pipeline_to_ground_truth = compare_activities(
        pipeline_df, ground_truth_df
    )

    matching_perc_ground_truth_to_pipeline = compare_activities(
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


def compare_activities(self, input_df, comparison_basis_df):
    total_matching_activities = 0
    for index, activity in enumerate(input_df["activity"]):
        total_matching_activities += find_activity(activity, comparison_basis_df, index)
        time.sleep(2)
    matching_percentage = round(total_matching_activities / input_df.shape[0], 2)
    matching_percentage = round(matching_percentage * 100, 0)

    return matching_percentage


def find_activity(activity, comparison_basis_df, index):
    # We want to look at a snippet from the other dataframe where we take five activities into account
    # starting from the current index -2 and ending at the current index +2
    # (writing +3 as python is exclusive on the upper bound)
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
