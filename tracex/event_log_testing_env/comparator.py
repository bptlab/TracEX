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
def execute(view, pipeline_df, ground_truth_df):
    """Compares the output of the pipeline against the ground truth."""
    mapping_ground_truth_to_data = (
        []
    )  # for each activity in the ground truth, the index of the corresponding activity in the data from the pipeline
    mapping_data_to_ground_truth = (
        []
    )  # for each activity in the data from the pipeline, the index of the corresponding activity in the ground truth

    compare_activities_dict = compare_activities_by_similarity(
        pipeline_df["activity"],
        ground_truth_df["activity"],
        mapping_data_to_ground_truth,
        mapping_ground_truth_to_data,
    )
    missing_activity_dict = find_missing_activities(
        ground_truth_df["activity"], mapping_ground_truth_to_data
    )
    missing_unexpected_activities_dict = find_unexpected_activities(
        pipeline_df["activity"], mapping_data_to_ground_truth
    )
    wrong_orders_dict = find_wrong_orders(
        pipeline_df["activity"], mapping_ground_truth_to_data
    )

    results_dict = {
        **compare_activities_dict,
        **missing_activity_dict,
        **missing_unexpected_activities_dict,
        **wrong_orders_dict,
    }

    return results_dict


def compare_activities_by_similarity(
    pipeline_activities,
    ground_truth_activities,
    mapping_data_to_ground_truth,
    mapping_ground_truth_to_data,
):
    matching_percent_pipeline_to_ground_truth = compare_activities(
        pipeline_activities, ground_truth_activities, mapping_data_to_ground_truth
    )
    print("50% done.")
    matching_percent_ground_truth_to_pipeline = compare_activities(
        ground_truth_activities, pipeline_activities, mapping_ground_truth_to_data
    )

    compare_activities_dict = {
        "matching_percent_pipeline_to_ground_truth": matching_percent_pipeline_to_ground_truth,
        "matching_percent_ground_truth_to_pipeline": matching_percent_ground_truth_to_pipeline,
        "mapping_data_to_ground_truth": mapping_data_to_ground_truth,
        "mapping_ground_truth_to_data": mapping_ground_truth_to_data,
    }

    return compare_activities_dict


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

        if "True" in response:
            mapping_input_to_comparison.append(lower + count)
            return
    mapping_input_to_comparison.append(-1)


def find_missing_activities(ground_truth_activities, mapping_ground_truth_to_data):
    missing_activites = []

    for count, value in enumerate(mapping_ground_truth_to_data):
        if value == -1:
            missing_activites.append(ground_truth_activities[count])

    missing_activities_dict = {
        "number_of_missing_activities": len(missing_activites),
        "missing_activities": missing_activites,
    }

    return missing_activities_dict


def find_unexpected_activities(df_activities, mapping_data_to_ground_truth):
    unexpteced_activities = []

    for count, value in enumerate(mapping_data_to_ground_truth):
        if value == -1:
            unexpteced_activities.append(df_activities[count])

    unexpected_activities_dict = {
        "number_of_unexpected_activities": len(unexpteced_activities),
        "unexpected_activities": unexpteced_activities,
    }

    return unexpected_activities_dict


def find_wrong_orders(df_activities, mapping_ground_truth_to_data):
    wrong_orders = []
    for index, first_activity in enumerate(mapping_ground_truth_to_data):
        if first_activity == -1:
            continue
        for second_activity in mapping_ground_truth_to_data[index:]:
            if second_activity == -1:
                continue
            if first_activity > second_activity:
                wrong_orders.append(
                    (df_activities[second_activity], df_activities[first_activity])
                )

    wrong_orders_dict = {
        "number_of_wrong_orders": len(wrong_orders),
        "wrong_orders": wrong_orders,
    }

    return wrong_orders_dict
