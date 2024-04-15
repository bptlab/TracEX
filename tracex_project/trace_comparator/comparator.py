"""This module compares an event log created by the pipeline against a manually created ground truth."""
import time
from pathlib import Path
from django.conf import settings

from trace_comparator import prompts as p
from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u


@log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
def compare_traces(view, pipeline_df, ground_truth_df):
    """Compares the output of the pipeline against the ground truth."""
    pipeline_activities = pipeline_df["activity"]
    ground_truth_activities = ground_truth_df["activity"]

    (
        mapping_data_to_ground_truth,
        mapping_ground_truth_to_data,
    ) = find_activity_mapping(pipeline_activities, ground_truth_activities)
    missing_activities = find_unmapped_activities(
        ground_truth_activities, mapping_ground_truth_to_data
    )
    unexpected_activities = find_unmapped_activities(
        pipeline_activities, mapping_data_to_ground_truth
    )
    wrong_orders = find_wrong_orders(pipeline_activities, mapping_ground_truth_to_data)

    matching_percent_pipeline_to_ground_truth = find_matching_percentage(
        pipeline_activities, mapping_data_to_ground_truth
    )
    matching_percent_ground_truth_to_pipeline = find_matching_percentage(
        ground_truth_activities, mapping_ground_truth_to_data
    )

    results_dict = {
        "mapping_data_to_ground_truth": mapping_data_to_ground_truth,
        "mapping_ground_truth_to_data": mapping_ground_truth_to_data,
        "missing_activities": missing_activities,
        "unexpected_activities": unexpected_activities,
        "wrong_orders": wrong_orders,
        "matching_percent_pipeline_to_ground_truth": matching_percent_pipeline_to_ground_truth,
        "matching_percent_ground_truth_to_pipeline": matching_percent_ground_truth_to_pipeline,
    }

    return results_dict


def find_activity_mapping(
    pipeline_activities,
    ground_truth_activities,
):
    mapping_data_to_ground_truth = compare_activities(
        pipeline_activities, ground_truth_activities
    )
    mapping_ground_truth_to_data = compare_activities(
        ground_truth_activities, pipeline_activities
    )
    (
        mapping_data_to_ground_truth,
        mapping_ground_truth_to_data,
    ) = postprocess_mappings(mapping_data_to_ground_truth, mapping_ground_truth_to_data)

    return mapping_data_to_ground_truth, mapping_ground_truth_to_data


def compare_activities(input_activities, comparison_basis_activities):
    mapping_input_to_comparison = []
    for index, activity in enumerate(input_activities):
        find_activity(
            activity,
            comparison_basis_activities,
            index,
            mapping_input_to_comparison,
        )
        time.sleep(2)
    return mapping_input_to_comparison


def find_activity(
    activity, comparison_basis_activities, index, mapping_input_to_comparison
):
    lower, upper = get_snippet_bounds(index, len(comparison_basis_activities))
    possible_matches = []
    for count, second_activity in enumerate(comparison_basis_activities[lower:upper]):
        messages = p.COMPARE_MESSAGES[:]
        messages.append(
            {
                "role": "user",
                "content": f"First: {activity}\nSecond: {second_activity}",
            }
        )
        response, top_logprops = u.query_gpt(messages, logprobs=True, top_logprobs=1)
        linear_prop = u.calculate_linear_probability(top_logprops[0].logprob)
        if "True" in response:
            possible_matches.append((lower + count, linear_prop))
    if possible_matches:
        best_match = max(possible_matches, key=lambda x: x[1])
        if best_match[1] > 0.7:
            mapping_input_to_comparison.append(best_match)
            return
    mapping_input_to_comparison.append((-1, 0))


@staticmethod
def get_snippet_bounds(index, dataframe_length):
    half_snipet_size = min(max(2, dataframe_length // 20), 5)
    lower = max(0, index - half_snipet_size)
    upper = min(dataframe_length, index + half_snipet_size + 1)
    if index < half_snipet_size:
        upper += abs(index - half_snipet_size)
    return lower, upper


def postprocess_mappings(mapping_data_to_ground_truth, mapping_ground_truth_to_data):
    mapping_data_to_ground_truth = fill_mapping(
        mapping_data_to_ground_truth, mapping_ground_truth_to_data
    )
    mapping_ground_truth_to_data = fill_mapping(
        mapping_ground_truth_to_data, mapping_data_to_ground_truth
    )
    mapping_data_to_ground_truth = remove_probabilities(mapping_data_to_ground_truth)
    mapping_ground_truth_to_data = remove_probabilities(mapping_ground_truth_to_data)
    return mapping_data_to_ground_truth, mapping_ground_truth_to_data


@staticmethod
def fill_mapping(mapping_back_to_forth, mapping_forth_to_back):
    for index_forth, activity_index_forth in enumerate(mapping_back_to_forth):
        if activity_index_forth[0] == -1:
            possible_matches = []
            for index_back, activity_index_back in enumerate(mapping_forth_to_back):
                if activity_index_back[0] == index_forth:
                    possible_matches.append((index_back, activity_index_back[1]))
            if possible_matches:
                best_match = max(possible_matches, key=lambda x: x[1])
                mapping_back_to_forth[index_forth] = (best_match[0], 0)
    return mapping_back_to_forth


@staticmethod
def remove_probabilities(mapping):
    new_mapping = [elem[0] for elem in mapping]
    return new_mapping


@staticmethod
def find_matching_percentage(input_activities, mapping_input_to_comparison):
    total_matching_activities = len(
        [elem for elem in mapping_input_to_comparison if elem != -1]
    )
    matching_percentage = round(
        total_matching_activities / input_activities.shape[0] * 100
    )

    return matching_percentage


@staticmethod
def find_unmapped_activities(activities, mapping):
    return [
        activities[index]
        for index, match_index in enumerate(mapping)
        if match_index == -1
    ]


def find_wrong_orders(df_activities, mapping_ground_truth_to_data):
    wrong_orders_indizes = []
    wrong_orders_activities = []
    for index, first_activity_index in enumerate(mapping_ground_truth_to_data):
        if first_activity_index == -1:
            continue
        for second_activity_index in mapping_ground_truth_to_data[index:]:
            if second_activity_index == -1:
                continue
            if first_activity_index > second_activity_index:
                if not pair_exists(
                    wrong_orders_indizes,
                    (first_activity_index, second_activity_index),
                ):
                    wrong_orders_indizes.append(
                        (first_activity_index, second_activity_index)
                    )
    for first_activity_index, second_activity_index in wrong_orders_indizes:
        wrong_orders_activities.append(
            (
                df_activities[first_activity_index],
                df_activities[second_activity_index],
            )
        )
    return wrong_orders_activities


@staticmethod
def pair_exists(pair_list, new_pair):
    for pair in pair_list:
        if pair == new_pair:
            return True
    return False
