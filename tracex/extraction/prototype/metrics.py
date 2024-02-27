import pandas as pd
import numpy as np

from . import utils as u
from . import prompts as p
from . import input_handling as ih


def measure_activity_relevance(text):
    df = ih.convert_text_to_bulletpoints(text)
    df["relevance"] = df["activity"].apply(
        lambda activity: pd.Series(
            measure_activity_relevance(activity, text)
        )
    )

    return df


def rate_activity_relevance(activity, text):
    category_mapping = {
        "No Relevance": 0,
        "Low Relevance": 1,
        "Moderate Relevance": 2,
        "High Relevance": 3,
    }

    messages = [
        {"role": "system", "content": p.METRIC_ACTIVITY_CONTEXT},
        {
            "role": "user",
            "content": p.METRIC_ACTIVITY_CONTEXT
            + "\nThe bulletpoint: "
            + activity
            + "\nThe patient journey: "
            + text,
        },
    ]

    answer = u.query_gpt(messages)
    print(answer)

    for key in category_mapping.keys():
        if key in answer:
            category = key
            break

    relevance = category_mapping.get(category, 0)
    print(activity)
    print(category)
    print(relevance)

    return category


def measure_timestamps_correctness(text):
    df = ih.convert_text_to_bulletpoints(text)
    print(df)
    df = ih.add_start(text, df)
    print(df)
    df = ih.add_end(text, df)
    print(df)

    df[["timestamp_correctness", "correctness_confidence"]] = df.apply(
        lambda row: pd.Series(
            rate_timestamps_correctness(
                row["activity"], row["start"], row["end"], text
            )
        ),
        axis=1,
    )

    return df


def rate_timestamps_correctness(activity, start, end, text):
    messages = [
        {"role": "system", "content": p.METRIC_TIMESTAMPS_CONTEXT},
        {
            "role": "user",
            "content": p.METRIC_TIMESTAMPS_PROMPT
            + "\nThe bulletpoint: "
            + activity
            + "\nThe start date related to the bulletpoint: "
            + start
            + "\nThe end date to the bulletpoint: "
            + end
            + "\nThe patient journey you should check the timestamps for the bulletpoint: "
            + text,
        },
    ]

    timestamp_correctness, top_logprops = u.query_gpt(
        messages, logprobs=True, top_logprobs=1
    )
    lin_prop = calculate_linear_probability(top_logprops[0].logprob)

    return (timestamp_correctness, lin_prop)


def measure_event_types_confidence(text):
    df = ih.convert_text_to_bulletpoints(text)

    df[["event_type", "(token_1, lin_prob_1)", "(token_2, lin_prob_2)"]] = df[
        "activity"
    ].apply(
        lambda activity: pd.Series(
            rate_event_type_confidence(activity)
        )
    )

    return df


def rate_event_type_confidence(activity):
    messages = [
        {"role": "system", "content": p.EVENT_TYPE_CONTEXT},
        {
            "role": "user",
            "content": p.EVENT_TYPE_PROMPT + "\nThe bulletpoint: " + activity,
        },
        {"role": "assistant", "content": p.EVENT_TYPE_ANSWER},
    ]

    event_type, top_logprops = u.query_gpt(messages, logprobs=True, top_logprobs=2)
    token1 = top_logprops[0].token
    lin_prob1 = calculate_linear_probability(top_logprops[0].logprob)
    token_2 = top_logprops[1].token
    lin_prob2 = calculate_linear_probability(top_logprops[1].logprob)

    return (event_type, (token1, lin_prob1), (token_2, lin_prob2))


def measure_location_confidence(text):
    df = ih.add_event_types(ih.convert_text_to_bulletpoints(text))
    df[["location", "(token_1, lin_prob_1)", "(token_2, lin_prob_2)"]] = df.apply(
        lambda row: pd.Series(
            rate_location_confidence(row["activity"], row["event_type"])
        ),
        axis=1,
    )

    return df


def rate_location_confidence(activity, event_type):
    messages = [
        {"role": "system", "content": p.LOCATION_CONTEXT},
        {
            "role": "user",
            "content": p.LOCATION_PROMPT
            + activity
            + "\nThe category: "
            + event_type,
        },
        {"role": "assistant", "content": p.LOCATION_ANSWER},
    ]
    location, top_logprops = u.query_gpt(messages, logprobs=True, top_logprobs=2)
    token_1 = top_logprops[0].token
    lin_prob_1 = calculate_linear_probability(top_logprops[0].logprob)
    token_2 = top_logprops[1].token
    lin_prob_2 = calculate_linear_probability(top_logprops[1].logprob)

    return (location, (token_1, lin_prob_1), (token_2, lin_prob_2))


def calculate_linear_probability(logprob):
    linear_prob = np.round(np.exp(logprob), 2)
    return linear_prob


def compare_given_to_manual(given_dataframe, manual_dataframe):
    with open(u.output_path / "compare.txt", "w") as f:
        f.write(" ")
    value = 0
    for activity in given_dataframe["activity"]:
        value += find_activity(activity, manual_dataframe)
    return value / given_dataframe.shape[0]


def compare_manual_to_given(manual_dataframe, given_dataframe):
    with open(u.output_path / "compare.txt", "w") as f:
        f.write(" ")
    value = 0
    for activity in manual_dataframe["activity"]:
        value += find_activity(activity, given_dataframe)
    return value / manual_dataframe.shape[0]


def find_activity(given_activity, comparative_dataframe):
    for row in comparative_dataframe["activity"]:
        message = [
            {"role": "system", "content": p.COMPARE_CONTEXT},
            {
                "role": "user",
                "content": p.COMPARE_PROMPT + given_activity + "\n" + row,
            },
        ]
        response = u.query_gpt(messages=message)
        with open(u.output_path / "compare.txt", "a") as f:
            f.write(
                given_activity
                + " verglichen mit: "
                + row
                + ":\n\n"
                + response
                + "\n\n\n"
            )
        if "True" in response:
            return 1
    return 0


def compare_to_test_1(dataframe):
    manual = pd.read_csv(u.comparison_path / "test_1_comparison_basis.csv")
    given_to_manual = compare_given_to_manual(dataframe, manual)
    print(
        "Prozent an gefundenen Stichpunkten, die in den Soll-Punkten enthalten sind: "
        + str(given_to_manual)
    )
    manual_to_given = compare_manual_to_given(manual, dataframe)
    print(
        "Prozent an Soll-Punkten, die in den gefundenen Stichpunkten enthalten sind: "
        + str(manual_to_given)
    )
    return 0


def compare_to_test_2(dataframe):
    manual = pd.read_csv(u.comparison_path / "test_2_comparison_basis.csv")
    given_to_manual = compare_given_to_manual(dataframe, manual)
    print(
        "Prozent an gefundenen Stichpunkten, die in den Soll-Punkten enthalten sind: "
        + str(given_to_manual)
    )
    manual_to_given = compare_manual_to_given(manual, dataframe)
    print(
        "Prozent an Soll-Punkten, die in den gefundenen Stichpunkten enthalten sind: "
        + str(manual_to_given)
    )
    return 0
