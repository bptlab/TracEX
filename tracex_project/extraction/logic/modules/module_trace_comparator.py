"""This module compares an event log created by the pipeline against a manually created ground truth."""
import time
from pathlib import Path
import pandas as pd
from django.conf import settings

from extraction.logic.module import Module
from extraction.logic import prompts as p
from tracex.logic.logger import log_execution_time
from tracex.logic import utils as u
from tracex.logic import constants as c


class TraceComparator(Module):
    """
    This is the module that compares the trace created by the pipeline
    against a manually created ground truth. We provide four different traces
    with the according patient journey as a ground truth in
    tracex/extraction/content/comparison.
    """

    def __init__(self):
        super().__init__()
        self.name = "Trace Comparator"
        self.description = "Compares the output of the pipeline against a ground truth."

    @log_execution_time(Path(settings.BASE_DIR / "tracex/logs/execution_time.log"))
    def execute(self, df, patient_journey=None, patient_journey_sentences=None):
        super().execute(df, patient_journey, patient_journey_sentences)

        return self.__compare_traces(df)

    def __compare_traces(self, df):
        ground_truth_df = pd.read_csv(
            c.comparison_path / "journey_test_4_comparison_basis.csv"
        )

        # for each activity in the ground truth, the index of the corresponding activity in the data from the pipeline
        mapping_groundtruth_to_data = []
        # for each activity in the data from the pipeline, the index of the corresponding activity in the ground truth
        mapping_data_to_groundtruth = []

        pipeline_activities = df["activity"]
        ground_truth_activities = ground_truth_df["activity"]

        (
            mapping_data_to_groundtruth,
            mapping_groundtruth_to_data,
        ) = self.__find_activity_mapping(
            pipeline_activities,
            ground_truth_activities,
            mapping_data_to_groundtruth,
            mapping_groundtruth_to_data,
        )
        missing_activities = self.__find_missing_activities(
            ground_truth_activities, mapping_groundtruth_to_data
        )
        unexpected_activities = self.__find_unexpected_activities(
            pipeline_activities, mapping_data_to_groundtruth
        )
        wrong_orders = self.__find_wrong_orders(
            pipeline_activities, mapping_groundtruth_to_data
        )

        matching_percent_pipeline_to_ground_truth = self.__find_matching_percentage(
            pipeline_activities, mapping_data_to_groundtruth
        )
        matching_percent_ground_truth_to_pipeline = self.__find_matching_percentage(
            ground_truth_activities, mapping_groundtruth_to_data
        )

        self.__document(
            matching_percent_pipeline_to_ground_truth,
            matching_percent_ground_truth_to_pipeline,
            pipeline_activities,
            ground_truth_activities,
            mapping_data_to_groundtruth,
            mapping_groundtruth_to_data,
            missing_activities,
            unexpected_activities,
            wrong_orders,
        )

        return df

    def __find_activity_mapping(
        self,
        pipeline_activities,
        ground_truth_activities,
        mapping_data_to_groundtruth,
        mapping_groundtruth_to_data,
    ):
        self.__compare_activities(
            pipeline_activities, ground_truth_activities, mapping_data_to_groundtruth
        )
        self.__compare_activities(
            ground_truth_activities, pipeline_activities, mapping_groundtruth_to_data
        )
        (
            mapping_data_to_groundtruth,
            mapping_groundtruth_to_data,
        ) = self.__postprocess_mappings(
            mapping_data_to_groundtruth, mapping_groundtruth_to_data
        )

        return mapping_data_to_groundtruth, mapping_groundtruth_to_data

    def __compare_activities(
        self, input_activities, comparison_basis_activities, mapping_input_to_comparison
    ):
        for index, activity in enumerate(input_activities):
            self.__find_activity(
                activity,
                comparison_basis_activities,
                index,
                mapping_input_to_comparison,
            )
            time.sleep(2)

    def __find_activity(
        self, activity, comparison_basis_activities, index, mapping_input_to_comparison
    ):
        lower, upper = self.__get_snippet_bounds(
            index, len(comparison_basis_activities)
        )
        possible_matches = []
        for count, second_activity in enumerate(
            comparison_basis_activities[lower:upper]
        ):
            messages = p.COMPARE_MESSAGES[:]
            messages.append(
                {
                    "role": "user",
                    "content": f"First: {activity}\nSecond: {second_activity}",
                }
            )
            response, top_logprops = u.query_gpt(
                messages, logprobs=True, top_logprobs=1
            )
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
    def __get_snippet_bounds(index, dataframe_length):
        half_snipet_size = min(max(2, dataframe_length // 20), 5)
        lower = max(0, index - half_snipet_size)
        upper = min(dataframe_length, index + half_snipet_size + 1)
        if index < half_snipet_size:
            upper += abs(index - half_snipet_size)
        return lower, upper

    def __postprocess_mappings(
        self, mapping_data_to_groundtruth, mapping_groundtruth_to_data
    ):
        mapping_data_to_groundtruth = self.__fill_mapping(
            mapping_data_to_groundtruth, mapping_groundtruth_to_data
        )
        mapping_groundtruth_to_data = self.__fill_mapping(
            mapping_groundtruth_to_data, mapping_data_to_groundtruth
        )
        mapping_data_to_groundtruth = self.__remove_probabilities(
            mapping_data_to_groundtruth
        )
        mapping_groundtruth_to_data = self.__remove_probabilities(
            mapping_groundtruth_to_data
        )
        return mapping_data_to_groundtruth, mapping_groundtruth_to_data

    @staticmethod
    def __fill_mapping(mapping_back_to_forth, mapping_forth_to_back):
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
    def __remove_probabilities(mapping):
        new_mapping = [elem[0] for elem in mapping]
        return new_mapping

    @staticmethod
    def __find_matching_percentage(input_activities, mapping_input_to_comparison):
        total_matching_activities = len(
            [elem for elem in mapping_input_to_comparison if elem != -1]
        )
        matching_percentage = round(
            total_matching_activities / input_activities.shape[0], 3
        )
        matching_percentage = round(matching_percentage * 100, 0)

        return matching_percentage

    @staticmethod
    def __find_missing_activities(ground_truth_activities, mapping_groundtruth_to_data):
        missing_activities = []
        for index, value in enumerate(mapping_groundtruth_to_data):
            if value == -1:
                missing_activities.append(ground_truth_activities[index])
        return missing_activities

    @staticmethod
    def __find_unexpected_activities(df_activities, mapping_data_to_groundtruth):
        unexpected_activities = []
        for count, value in enumerate(mapping_data_to_groundtruth):
            if value == -1:
                unexpected_activities.append(df_activities[count])
        return unexpected_activities

    def __find_wrong_orders(self, df_activities, mapping_groundtruth_to_data):
        wrong_orders_indizes = []
        wrong_orders_activities = []
        for index, first_activity_index in enumerate(mapping_groundtruth_to_data):
            if first_activity_index == -1:
                continue
            for second_activity_index in mapping_groundtruth_to_data[index:]:
                if second_activity_index == -1:
                    continue
                if first_activity_index > second_activity_index:
                    if not self.__pair_exists(
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
    def __pair_exists(pair_list, new_pair):
        for pair in pair_list:
            if pair == new_pair:
                return True
        return False

    @staticmethod
    def __document(
        matching_percent_pipeline_to_ground_truth,
        matching_percent_ground_truth_to_pipeline,
        pipeline_activities,
        ground_truth_activities,
        mapping_data_to_groundtruth,
        mapping_groundtruth_to_data,
        missing_activities,
        unexpected_activities,
        wrong_orders,
    ):
        with open(c.output_path / "event_log_comparison.txt", "w") as f:
            f.write("Activities from the pipeline output:\n\n")
            for index, activity in enumerate(pipeline_activities):
                f.write(f"{index}: {activity}\n")
            f.write("\n\nActivities from the ground truth:\n\n")
            for index, activity in enumerate(ground_truth_activities):
                f.write(f"{index}: {activity}\n")
            f.write("\n\nMapping from pipeline to ground truth:\n\n")
            for index, value in enumerate(mapping_data_to_groundtruth):
                if value != -1:
                    f.write(
                        f'"{pipeline_activities[index]}": "{ground_truth_activities[value]}"\n'
                    )
                else:
                    f.write(f'"{pipeline_activities[index]}": "-"\n')
            f.write("\n\nMapping from ground truth to pipeline:\n\n")
            for index, value in enumerate(mapping_groundtruth_to_data):
                if value != -1:
                    f.write(
                        f'"{ground_truth_activities[index]}": "{pipeline_activities[value]}"\n'
                    )
                else:
                    f.write(f'"{ground_truth_activities[index]}": "-"\n')

            f.write(
                "\n\nPercentage of activities found by the pipeline that are contained in ground truth: "
                + str(matching_percent_pipeline_to_ground_truth)
                + "%\n\n"
            )
            f.write(
                "Percentage of activities contained in ground truth that are found by the pipeline: "
                + str(matching_percent_ground_truth_to_pipeline)
                + "%\n"
            )

            f.write(
                f"\n\nMissing activities in the pipeline: {len(missing_activities)}\n"
            )
            for missing_activity in missing_activities:
                f.write(f'"{missing_activity}"\n')
            f.write(
                f"\n\nUnexpected activities in the pipeline: {len(unexpected_activities)}\n"
            )
            for unexpected_activity in unexpected_activities:
                f.write(f'"{unexpected_activity}"\n')
            f.write(f"\n\nWrong orders in the pipeline: {len(wrong_orders)}\n")
            for first_activity, second_activity in wrong_orders:
                f.write(f'"{second_activity}" should come before "{first_activity}"\n')
