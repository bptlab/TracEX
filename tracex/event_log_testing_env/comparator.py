"""This module compares an event log created by the pipeline against a manually created ground truth."""
import time
from pathlib import Path
import pandas as pd
from django.conf import settings

from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u
from tracex.logic import constants as c
from . import prompts as p


@log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
def execute(pipeline_df, ground_truth_df):
    """Compares the output of the pipeline against the ground truth."""
    mapping_groundtruth_to_data = (
        []
    )  # for each activity in the ground truth, the index of the corresponding activity in the data from the pipeline
    mapping_data_to_groundtruth = (
        []
    )  # for each activity in the data from the pipeline, the index of the corresponding activity in the ground truth

    compare_activities_by_similarity(
        pipeline_df["activity"],
        ground_truth_df["activity"],
        mapping_data_to_groundtruth,
        mapping_groundtruth_to_data,
    )
    find_missing_activities(ground_truth_df["activity"], mapping_groundtruth_to_data)
    find_unexpected_activities(pipeline_df["activity"], mapping_data_to_groundtruth)
    find_wrong_orders(pipeline_df["activity"], mapping_groundtruth_to_data)

    return pipeline_df


def compare_activities_by_similarity(
    pipeline_activities,
    ground_truth_activities,
    mapping_data_to_groundtruth,
    mapping_groundtruth_to_data,
):
    with open(c.output_path / "compare.txt", "w") as f:
        f.write("Activity comparisons\n\n")

    matching_percent_pipeline_to_ground_truth = compare_activities(
        pipeline_activities, ground_truth_activities, mapping_data_to_groundtruth
    )
    print("50% done.")
    matching_percent_ground_truth_to_pipeline = compare_activities(
        ground_truth_activities, pipeline_activities, mapping_groundtruth_to_data
    )
    with open(c.output_path / "event_log_comparison.txt", "w") as f:
        f.write(
            "Percentage of activities found by the pipeline that are contained in ground truth: "
            + str(matching_percent_pipeline_to_ground_truth)
            + "%\n\n"
        )
        f.write(
            "Percentage of activities contained in ground truth that are found by the pipeline: "
            + str(matching_percent_ground_truth_to_pipeline)
            + "%\n"
        )

    with open(c.output_path / "compare.txt", "a") as f:
        f.write("Activities from the pipeline output:\n\n")
        for activity in pipeline_activities:
            f.write(f"{activity}\n")
        f.write("\n\nActivities from the ground truth:\n\n")
        for activity in ground_truth_activities:
            f.write(f"{activity}\n")
        f.write("\n\nMapping from pipeline to ground truth:\n\n")
        for index, value in enumerate(mapping_data_to_groundtruth):
            if value != -1:
                f.write(
                    f'"{pipeline_activities[index]}": "{ground_truth_activities[value]}"\n'
                )
        f.write("\n\nMapping from ground truth to pipeline:\n\n")
        for index, value in enumerate(mapping_groundtruth_to_data):
            if value != -1:
                f.write(
                    f'"{ground_truth_activities[index]}": "{pipeline_activities[value]}"\n'
                )


def compare_activities(
    input_activities, comparison_basis_activities, mapping_input_to_comparison
):
    for index, activity in enumerate(input_activities):
        find_activity(
            activity,
            comparison_basis_activities,
            index,
            mapping_input_to_comparison,
        )
        time.sleep(2)
    total_matching_activities = len(
        [elem for elem in mapping_input_to_comparison if elem != -1]
    )
    matching_percentage = round(
        total_matching_activities / input_activities.shape[0], 3
    )
    matching_percentage = round(matching_percentage * 100, 0)

    return matching_percentage


@staticmethod
def find_activity(
    activity, comparison_basis_activities, index, mapping_input_to_comparison
):
    lower = max(0, index - 2)
    upper = min(len(comparison_basis_activities), index + 3)
    for count, second_activity in enumerate(comparison_basis_activities[lower:upper]):
        messages = p.COMPARE_MESSAGES[:]
        messages.append(
            {
                "role": "user",
                "content": f"First: {activity}\nSecond: {second_activity}",
            }
        )
        response = u.query_gpt(messages)

        with open(c.output_path / "compare.txt", "a") as f:
            f.write(f'"{activity}" compared with: "{second_activity}"\n{response}\n\n')

        if "True" in response:
            mapping_input_to_comparison.append(lower + count)
            return
    mapping_input_to_comparison.append(-1)


@staticmethod
def find_missing_activities(ground_truth_activities, mapping_groundtruth_to_data):
    number_of_missing_activities = len(
        [elem for elem in mapping_groundtruth_to_data if elem == -1]
    )
    with open(c.output_path / "event_log_comparison.txt", "a") as f:
        f.write(
            f"\nMissing activities in the pipeline: {number_of_missing_activities}\n"
        )

    for count, value in enumerate(mapping_groundtruth_to_data):
        if value == -1:
            with open(c.output_path.joinpath("event_log_comparison.txt"), "a") as f:
                f.write(f"{ground_truth_activities[count]}\n")


@staticmethod
def find_unexpected_activities(df_activities, mapping_data_to_groundtruth):
    number_of_unexpected_activities = len(
        [elem for elem in mapping_data_to_groundtruth if elem == -1]
    )
    with open(c.output_path / "event_log_comparison.txt", "a") as f:
        f.write(
            f"\nUnexpected activities in the pipeline: {number_of_unexpected_activities}\n"
        )

    for count, value in enumerate(mapping_data_to_groundtruth):
        if value == -1:
            with open(c.output_path.joinpath("event_log_comparison.txt"), "a") as f:
                f.write(f"{df_activities[count]}\n")


@staticmethod
def find_wrong_orders(df_activities, mapping_groundtruth_to_data):
    wrong_orders = []
    for index, first_activity in enumerate(mapping_groundtruth_to_data):
        if first_activity == -1:
            continue
        for second_activity in mapping_groundtruth_to_data[index:]:
            if second_activity == -1:
                continue
            if first_activity > second_activity:
                wrong_orders.append((first_activity, second_activity))
    with open(c.output_path / "event_log_comparison.txt", "a") as f:
        f.write(f"\nWrong orders in the pipeline: {len(wrong_orders)}\n")
        for first_activity, second_activity in wrong_orders:
            f.write(
                f'"{df_activities[second_activity]}" should come before "{df_activities[first_activity]}"\n'
            )
