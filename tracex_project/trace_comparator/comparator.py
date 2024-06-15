"""The trace comparator compares the pipeline output against a ground truth and vice versa."""
import time
from typing import List, Tuple
from pathlib import Path
from django.conf import settings
import pandas as pd

from extraction.models import Prompt
from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u, constants as c


@log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
def compare_traces(
    view, pipeline_df: pd.DataFrame, ground_truth_df: pd.DataFrame
) -> dict:
    """Executes the trace comparison.

    Compare the piepline output to the ground truth and determine all matching activities.Classify every activity
    from the pipeline output that has no match as 'missing' and every activity from the ground truth that
    has no match as 'unexpected'. Finally, determine activities from the pipeline that are correctly
    matched but in the wrong order.
    """
    if c.TEST_MODE:
        simulate_progress(view)

        mapping_pipeline_to_ground_truth = [0, -1, -1, 2, 5, 4, 4, -1, -1, -1, 12, 13, 12, 15]
        mapping_ground_truth_to_pipeline = [0, 4, 3, 5, 5, 4, -1, -1, -1, -1, -1, 13, 10, 11, -1, 13, 12, -1]
        missing_activities = ['getting tested for covid 19 in local testing center', 'testing positive for covid 19', 'focusing on resting while isolated', 'receiving emotional support from family', 'experiencing slow recovery', 'remainding optimistic and adhering to safety guidelines', 'feeling thankful for healthcare personal']
        unexpected_activities = ['consulting doctor', 'getting tested for Covid-19', 'recovering with family support', 'returning to work with precautions', 'decision to get vaccinated']
        wrong_orders = [('advised home quarantine and treatment', 'receiving positive test results'), ('receiving care from family', 'advised home quarantine and treatment'), ('feeling relief and hope post-vaccination', 'receiving first dose of vaccine'), ('feeling relief and hope post-vaccination', 'experiencing mild side effects'), ('feeling relief and hope post-vaccination', 'receiving second dose of vaccine')]
        matching_percent_ground_truth_to_pipeline = 64
        matching_percent_pipeline_to_ground_truth = 61

    
    else:
        pipeline_activities: pd.Series = pipeline_df["activity"]
        ground_truth_activities: pd.Series = ground_truth_df["activity"]

        (
            mapping_pipeline_to_ground_truth,
            mapping_ground_truth_to_pipeline,
        ) = find_activity_mapping(view, pipeline_activities, ground_truth_activities)
        missing_activities: List[str] = find_unmapped_activities(
            ground_truth_activities, mapping_ground_truth_to_pipeline
        )
        unexpected_activities: List[str] = find_unmapped_activities(
            pipeline_activities, mapping_pipeline_to_ground_truth
        )
        wrong_orders: List[Tuple[str, str]] = find_wrong_orders(
            pipeline_activities, mapping_ground_truth_to_pipeline
        )

        matching_percent_pipeline_to_ground_truth: int = find_matching_percentage(
            pipeline_activities, mapping_pipeline_to_ground_truth
        )
        matching_percent_ground_truth_to_pipeline: int = find_matching_percentage(
            ground_truth_activities, mapping_ground_truth_to_pipeline
        )

    results: dict = {
        "mapping_pipeline_to_ground_truth": mapping_pipeline_to_ground_truth,
        "mapping_ground_truth_to_pipeline": mapping_ground_truth_to_pipeline,
        "missing_activities": missing_activities,
        "unexpected_activities": unexpected_activities,
        "wrong_orders": wrong_orders,
        "matching_percent_pipeline_to_ground_truth": matching_percent_pipeline_to_ground_truth,
        "matching_percent_ground_truth_to_pipeline": matching_percent_ground_truth_to_pipeline,
    }

    print(results)
    return results


def simulate_progress(view):
        count = 0
        while count <= 50:
            count += 5
            time.sleep(1)
            update_progress(
                view, count, 100, "Mapping Pipeline Activites to Ground Truth Activites"
            )

        while count <= 100:
            count += 5
            time.sleep(1)
            update_progress(
                view, count, 100, "Mapping Ground Truth Activites to Pipeline Activites"
            )

def find_activity_mapping(
    view, pipeline_activities: pd.Series, ground_truth_activities: pd.Series
) -> Tuple[List[int], List[int]]:
    """Create a mapping of activities from the pipeline to the ground truth and vice versa."""
    total_steps: int = len(pipeline_activities) + len(ground_truth_activities)
    half_progress: int = len(pipeline_activities)

    mapping_pipeline_to_ground_truth = compare_activities(
        view,
        0,
        total_steps,
        "Mapping pipeline activities to ground truth activities",
        pipeline_activities,
        ground_truth_activities,
    )
    mapping_ground_truth_to_pipeline = compare_activities(
        view,
        half_progress,
        total_steps,
        "Mapping ground truth activities to pipeline activities",
        ground_truth_activities,
        pipeline_activities,
    )

    (
        mapping_pipeline_to_ground_truth,
        mapping_ground_truth_to_pipeline,
    ) = postprocess_mappings(
        mapping_pipeline_to_ground_truth, mapping_ground_truth_to_pipeline
    )

    return mapping_pipeline_to_ground_truth, mapping_ground_truth_to_pipeline


def compare_activities(
    view,
    current_step: int,
    total_steps: int,
    status: str,
    input_activities: pd.Series,
    comparison_basis_activities: pd.Series,
) -> List[Tuple[int, float]]:
    """Compare input activities with ground truth activities."""
    mapping_input_to_comparison: List[Tuple[int, float]] = []
    for index, activity in enumerate(input_activities):
        update_progress(view, current_step, total_steps, status)
        find_activity(
            activity,
            comparison_basis_activities,
            index,
            mapping_input_to_comparison,
        )
        time.sleep(2)  # this prevents the token limit per minute from being exceeded
        current_step += 1

    return mapping_input_to_comparison


def find_activity(
    activity,
    comparison_basis_activities: pd.Series,
    activity_index: int,
    mapping_input_to_comparison: List[Tuple[int, float]],
) -> None:
    """Compares an activity against potential matches to identify the best match based on
    similarity.

    An activity from the newly made extraction is compared against each activity from the ground truth that within a
    certain range. For instance, an activity with index 5 ist compared to activities 3-7 from the ground truth. Both
    activities are sent to the GPT model to determine if they are semantically similar.
    """
    lower, upper = u.get_snippet_bounds(
        activity_index, len(comparison_basis_activities)
    )
    possible_matches: List[Tuple[int, float]] = []
    for count, second_activity in enumerate(comparison_basis_activities[lower:upper]):
        messages = Prompt.objects.get(name="COMPARE_MESSAGES").text
        messages.append(
            {
                "role": "user",
                "content": f"First: {activity}\nSecond: {second_activity}",
            }
        )
        response, linear_probability = u.query_gpt(messages, return_linear_probability=True, top_logprobs=1)
        if "True" in response:
            possible_matches.append((lower + count, linear_probability))

    mapping_input_to_comparison.append(
        max(
            (
                (index, prob)
                for index, prob in possible_matches
                if prob > c.THRESHOLD_FOR_MATCH
            ),
            key=lambda x: x[1],
            default=(-1, 0),
        )
    )


def postprocess_mappings(
    mapping_data_to_ground_truth: List, mapping_ground_truth_to_data: List
) -> Tuple[List[int], List[int]]:
    """Postprocess the mappings between data and ground truth."""
    mapping_data_to_ground_truth = fill_mapping(
        mapping_data_to_ground_truth, mapping_ground_truth_to_data
    )
    mapping_ground_truth_to_data = fill_mapping(
        mapping_ground_truth_to_data, mapping_data_to_ground_truth
    )
    mapping_data_to_ground_truth = remove_probabilities(mapping_data_to_ground_truth)
    mapping_ground_truth_to_data = remove_probabilities(mapping_ground_truth_to_data)

    return mapping_data_to_ground_truth, mapping_ground_truth_to_data


def fill_mapping(mapping_back_to_forth: List, mapping_forth_to_back: List) -> List:
    """Fill up missing mappings using the reverse mapping and updates existing mappings, if ones with higher
    probabilities are found. If an activity has no mapping on either side, leave it as is.
    """
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


def remove_probabilities(mapping: List[Tuple[int, float]]) -> List[int]:
    """Remove the probabilities from the mapping."""
    new_mapping = [elem[0] for elem in mapping]

    return new_mapping


def find_matching_percentage(
    input_activities: pd.Series, mapping_input_to_comparison: list
) -> int:
    """Calculate the percentage of matching activities."""
    total_matching_activities: int = sum(
        1 for elem in mapping_input_to_comparison if elem != -1
    )
    matching_percentage: int = round(
        total_matching_activities / input_activities.shape[0] * 100
    )

    return matching_percentage


def find_unmapped_activities(activities: pd.Series, mapping: list) -> List[str]:
    """Find the activities that are not mapped, indicated by mapping index -1."""
    return [
        activities[index]
        for index, mapping_index in enumerate(mapping)
        if mapping_index == -1
    ]


def find_wrong_orders(
    df_activities: pd.Series, mapping_ground_truth_to_data: List[int]
) -> List[Tuple[str, str]]:
    """Find the activities that are in the wrong order.

    For every activity in the provided dataframe, the function checks if the mapped activity in the ground truth has a
    smaller index, indicating the activity should have been found earlier. All activities and their mapped counterparts
    from the ground truth are saved in a list and returned.
    """
    wrong_orders_indices: List[Tuple[int, int]] = []
    wrong_orders_activities: List[Tuple[str, str]] = []
    for index, first_activity_index in enumerate(mapping_ground_truth_to_data):
        if first_activity_index == -1:
            continue
        for second_activity_index in mapping_ground_truth_to_data[index:]:
            if second_activity_index == -1:
                continue
            if first_activity_index > second_activity_index:
                if not any(
                    pair == (first_activity_index, second_activity_index)
                    for pair in wrong_orders_indices
                ):
                    wrong_orders_indices.append(
                        (first_activity_index, second_activity_index)
                    )
    for first_activity_index, second_activity_index in wrong_orders_indices:
        wrong_orders_activities.append(
            (
                df_activities[first_activity_index],
                df_activities[second_activity_index],
            )
        )

    return wrong_orders_activities


def update_progress(view, current_step: int, total_steps: int, status: str) -> None:
    """Update the progress of the extraction, by updating the session variables."""
    if view is not None:
        percentage = round((current_step / total_steps) * 100)
        view.request.session["progress"] = percentage
        view.request.session["status"] = status
        view.request.session.save()
