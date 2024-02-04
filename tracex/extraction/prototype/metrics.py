import pandas as pd
import numpy as np

from . import utils as u
from . import prompts as p
from . import input_handling as ih


def measure_event_information_relevance(text):
    df = ih.convert_text_to_bulletpoints(text)
    df[["weighted_relevance", "relevance", "lin_prop"]] = df["event_information"].apply(
        lambda event_information: pd.Series(
            rate_event_information_relevance(event_information, text)
        )
    )

    return df


def rate_event_information_relevance(event_information, text):
    category_mapping = {
        "Not Relevant": 1,
        "Low Relevance": 2,
        "Moderate Relevance": 3,
        "High Relevance": 4,
        "Critical Relevance": 5,
    }

    messages = [
        {"role": "system", "content": p.METRIC_EVENT_INFORMATION_CONTEXT},
        {
            "role": "user",
            "content": p.METRIC_EVENT_INFORMATION_CONTEXT
            + "\nThe bulletpoint: "
            + event_information
            + "\nThe patient journey: "
            + text,
        },
    ]

    category, top_logprops = u.query_gpt(messages, logprobs=True, top_logprobs=1)
    relevance = category_mapping.get(category, "Category not found")
    lin_prop = calculate_linear_probability(top_logprops[0].logprob)
    weighted_relevance = relevance * lin_prop

    return (weighted_relevance, category, lin_prop)


def measure_timestamps_correctness(text):
    df = ih.convert_text_to_bulletpoints(text)
    print(df)
    df = ih.add_start_dates(text, df)
    print(df)
    df = ih.add_end_dates(text, df)
    print(df)

    df[["timestamp_correctness", "correctness_confidence"]] = df.apply(
        lambda row: pd.Series(
            rate_timestamps_correctness(
                row["event_information"], row["start_date"], row["end_date"], text
            )
        ),
        axis=1,
    )

    return df


def rate_timestamps_correctness(event_information, start_date, end_date, text):
    messages = [
        {"role": "system", "content": p.METRIC_TIMESTAMPS_CONTEXT},
        {
            "role": "user",
            "content": p.METRIC_TIMESTAMPS_PROMPT
            + "\nThe bulletpoint: "
            + event_information
            + "\nThe start date related to the bulletpoint: "
            + start_date
            + "\nThe end date to the bulletpoint: "
            + end_date
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
        "event_information"
    ].apply(
        lambda event_information: pd.Series(
            rate_event_type_confidence(event_information)
        )
    )

    return df


def rate_event_type_confidence(event_information):
    messages = [
        {"role": "system", "content": p.EVENT_TYPE_CONTEXT},
        {
            "role": "user",
            "content": p.EVENT_TYPE_PROMPT + "\nThe bulletpoint: " + event_information,
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
            rate_location_confidence(row["event_information"], row["event_type"])
        ),
        axis=1,
    )

    return df


def rate_location_confidence(event_information, event_type):
    messages = [
        {"role": "system", "content": p.LOCATION_CONTEXT},
        {
            "role": "user",
            "content": p.LOCATION_PROMPT
            + event_information
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
