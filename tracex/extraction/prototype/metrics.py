import pandas as pd
import numpy as np

from . import utils as u
from . import prompts as p
from . import input_handling as ih


def measure_event_types(text):
    df = ih.convert_text_to_bulletpoints(text)
    new_df = pd.DataFrame([], columns=["event_type", "(token1, lin_prob1)", "(token2, lin_prob2)"])
    values_list = df.values.tolist()
    for item in values_list:
        messages = [
            {"role": "system", "content": p.EVENT_TYPE_CONTEXT},
            {
                "role": "user",
                "content": p.EVENT_TYPE_PROMPT + "\nThe bulletpoint: " + item[0],
            },
            {"role": "assistant", "content": p.EVENT_TYPE_ANSWER},
        ]
        content, top_logprops = u.query_gpt(messages, logprobs=True, top_logprobs=2)
        metrics = [content]

        for logprob in top_logprops:
            token = logprob.token
            lin_prop = calculate_linear_probability(logprob.logprob)
            metrics.append((token, lin_prop))
        
        new_row = pd.DataFrame([metrics], columns=["event_type", "(token1, lin_prob1)", "(token2, lin_prob2)"])
        new_df = pd.concat([new_df, new_row], ignore_index=True)
        ih.document_intermediates(new_row.to_string())
        print(new_row.to_string())
    df = pd.concat([df, new_df], axis=1)
    return df

def measure_location(text):
    df = ih.add_event_types(ih.convert_text_to_bulletpoints(text))
    new_df = pd.DataFrame([], columns=["location", "(token1, lin_prob1)", "(token2, lin_prob2)"])
    values_list = df.values.tolist()
    event_type_key = df.columns.get_loc("event_type")
    for item in values_list:
        messages = [
            {"role": "system", "content": p.LOCATION_CONTEXT},
            {
                "role": "user",
                "content": p.LOCATION_PROMPT
                + item[0]
                + "\nThe category: "
                + item[event_type_key],
            },
            {"role": "assistant", "content": p.LOCATION_ANSWER},
        ]
        content, top_logprops = u.query_gpt(messages, logprobs=True, top_logprobs=2)
        metrics = [content]

        for logprob in top_logprops:
            token = logprob.token
            lin_prop = calculate_linear_probability(logprob.logprob)
            metrics.append((token, lin_prop))

        new_row = pd.DataFrame([metrics], columns=["location", "(token1, lin_prob1)", "(token2, lin_prob2)"])
        new_df = pd.concat([new_df, new_row], ignore_index=True)
        ih.document_intermediates(new_row.to_string())
    df = pd.concat([df, new_df], axis=1)
    return df




def calculate_linear_probability(logprob):
    linear_prob = np.round(np.exp(logprob) * 100, 2)
    return linear_prob
