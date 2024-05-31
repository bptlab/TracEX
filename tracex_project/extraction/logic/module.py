"""Module providing the abstract base class for all modules."""
from abc import ABC
from typing import Dict, List, Optional

import pandas as pd


class Module(ABC):
    """
    This abstract base class defines a common interface for all concrete modules.
    """

    def __init__(self):
        """
        Initializes a module with the following parameters.
            name: The name of the module.
            description: A description of what the module does.
            patient_journey: The Patient Journey most modules operate on.
            result: The result that the module provides.
        """
        self.name = None
        self.description = None
        self.patient_journey = None
        self.patient_journey_sentences = None
        self.cohort = None

    def execute(
        self,
        _input,
        *,
        patient_journey: Optional[str] = None,
        patient_journey_sentences: Optional[List[str]] = None,
        cohort: Optional[Dict[str, str]] = None,
    ) -> pd.DataFrame:
        """
        Executes the logic of the module. Override this to define your own module.

        Keyword arguments:
        _input -- Any additional input to the module.
        patient_journey -- The Patient Journey as text.
        patient_journey_sentences -- The same Patient Journey as a list of sentences.
        """
        self.patient_journey = patient_journey
        self.patient_journey_sentences = patient_journey_sentences
        self.cohort = cohort

        return pd.DataFrame()

    def execute_and_save(
        self,
        _input,
        *,
        patient_journey: Optional[str] = None,
        patient_journey_sentences: Optional[list[str]] = None,
    ) -> int:
        """
        Executes the logic of the module and saves the result to the database. Override this to define your own module.

        Keyword arguments:
        patient_journey -- The Patient Journey as text.
        patient_journey_sentences -- The same Patient Journey as a list of sentences.
        """
        self.patient_journey = patient_journey
        self.patient_journey_sentences = patient_journey_sentences

        return 0
