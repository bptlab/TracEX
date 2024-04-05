""""The event log comparator compares the event log created by the pipeline against a manually created ground truth."""
from pathlib import Path
import pandas as pd
from django.conf import settings

from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u
from tracex.logic import constants as c
from . import prompts as p


@log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
def comparing_event_logs(df, patient_journey_id):
    """Comparing event logs."""

    ground_truth_df = pd.read_csv(
        c.comparison_path / "journey_test_1_comparison_basis.csv"
    )

    return start_comparison(df, ground_truth_df)


def start_comparison(pipeline_df, ground_truth_df):
    matching_perc_pipeline_to_ground_truth = compare_activities(
        pipeline_df, ground_truth_df
    )

    matching_perc_ground_truth_to_pipeline = compare_activities(
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


def compare_activities(input_df, comparison_basis_df):
    total_matching_activities = 0
    for activity in input_df["activity"]:
        total_matching_activities += find_activity(activity, comparison_basis_df)
    matching_percentage = round(total_matching_activities / input_df.shape[0], 2)
    return matching_percentage


def find_activity(activity, comparison_basis_df):
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
