"""Module providing constants for the project."""
import time
from dataclasses import dataclass
from typing import Optional

from .constants import *
from openai import OpenAI


def pause_between_queries():
    """Pauses between queries."""
    time.sleep(5)


def get_decision(question):
    """Gets a decision from the user."""
    decision = input(question).lower()
    if decision == "y":
        return True
    if decision == "n":
        return False
    print("Please enter y or n.")
    return get_decision(question)


def query_gpt(messages, max_tokens=MAX_TOKENS, temperature=TEMPERATURE_SUMMARIZING):
    """Queries the GPT engine."""
    client = OpenAI(api_key=oaik)
    response = client.chat.completions.create(
        model=MODEL, messages=messages, max_tokens=max_tokens, temperature=temperature
    )
    output = response.choices[0].message.content
    return output


@dataclass
class ExtractionConfiguration:
    patient_journey: str
    event_types: list
    locations: list
    activity_key: Optional[str] = "event_type"

    def update(self, **kwargs):
        """Update the configuration with a dictionary."""
        for key, value in kwargs.items():
            setattr(self, key, value)
