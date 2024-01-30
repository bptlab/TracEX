"""Module providing functions for preprocessing the input."""
import pandas as pd

from . import utils as u
from . import prompts as p


def preprocessing_identify_time_specification(text):
    """Preprocesses the input so that mentioned durations and times are clearly displayed in the output."""
    messages = [
        {"role": "system", "content": p.SYSTEM_ROLE_PROMPT_IDENTIFY},
        {"role": "user", "content": p.USER_ROLE_PROMPT_IDENTIFY + text},
        {"role": "assistant", "content": p.ASSISTANT_ROLE_PROMPT_IDENTIFY},
    ]
    preprocessed_text = u.query_gpt(messages)

    return preprocessed_text


def preprocessing_spellcheck(text):
    """Preprocesses the input so that the text is spellchecked and grammatically correct."""
    messages = [
        {"role": "system", "content": p.SYSTEM_ROLE_PROMPT_SPELLCHECK},
        {"role": "user", "content": p.USER_ROLE_PROMPT_SPELLCHECK + text},
        {"role": "assistant", "content": p.ASSISTANT_ROLE_PROMPT_SPELLCHECK},
    ]
    preprocessed_text = u.query_gpt(messages)

    return preprocessed_text


def preprocessing_condense(text):
    """Preprocesses the input so that the text is condensed and shortened."""
    messages = [
        {"role": "system", "content": p.SYSTEM_ROLE_PROMPT_CONDENSE},
        {"role": "user", "content": p.USER_ROLE_PROMPT_CONDENSE + text},
        {"role": "assistant", "content": p.ASSISTANT_ROLE_PROMPT_CONDENSE},
    ]
    preprocessed_text = u.query_gpt(messages)

    return preprocessed_text


def preprocessing_timeline(text):
    """Adds a timeline to the input."""
    messages = [
        {"role": "system", "content": p.SYSTEM_ROLE_PROMPT_TIMELINE},
        {"role": "user", "content": p.USER_ROLE_PROMPT_TIMELINE + text},
        {"role": "assistant", "content": p.ASSISTANT_ROLE_PROMPT_TIMELINE},
    ]
    preprocessed_text = u.query_gpt(messages)

    return preprocessed_text


def preprocessing_timeline_chainofthought(text):
    """Adds a timeline to the input."""
    messages = [
        {"role": "system", "content": p.SYSTEM_ROLE_PROMPT_TIMELINE_CHAINOFTHOUGHT},
        {"role": "user", "content": p.USER_ROLE_PROMPT_TIMELINE_CHAINOFTHOUGHT_EXAMPLE},
        {
            "role": "assistant",
            "content": p.ASSISTANT_ROLE_PROMPT_TIMELINE_CHAINOFTHOUGHT,
        },
        {"role": "user", "content": p.USER_ROLE_PROMPT_TIMELINE_CHAINOFTHOUGHT + text},
    ]
    preprocessed_text = u.query_gpt(messages)

    return preprocessed_text
