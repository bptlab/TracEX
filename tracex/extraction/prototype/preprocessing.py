"""Module providing functions for preprocessing the input."""
import pandas as pd

from . import utils as u
from . import prompts as p


def refactor_input_journey_time(text):
    """Preprocesses the input so that mentioned durations and times are clearly displayed in the output."""
    messages = [
        {"role": "system", "content": p.REFACTOR_INPUT_JOURNEY_TIME_CONTEXT_3},
        {"role": "user", "content": p.REFACTOR_INPUT_JOURNEY_TIME_PROMPT + text},
        {"role": "assistant", "content": p.REFACTOR_INPUT_JOURNEY_TIME_ANSWER},
    ]
    preprocessed_text = u.query_gpt(messages)

    return preprocessed_text
