"""Module providing the abstract base class for all modules."""
from abc import ABC

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
            patient_journey: The patient journey most modules operate on.
            result: The result that the module provides.
        """
        self.name = None
        self.description = None
        self.patient_journey = None
        self.patient_journey_sentences = None

    def execute(self, _input, *, patient_journey=None, patient_journey_sentences=None) -> pd.DataFrame:
        """
        Executes the logic of the module. Override this to define your own module.
        Every module receives the patient journey as parameter which is set to the instance variable of each module.
        This method should always return a dataframe, so other modules can use the result.
        """
        print(f"Starting Module {self.name}.")
        self.patient_journey = patient_journey
        self.patient_journey_sentences = patient_journey_sentences

        return pd.DataFrame()

    def execute_and_save(self, _input, *, patient_journey=None, patient_journey_sentences=None) -> int:
        """
        Executes the logic of the module and saves the result to the database. Override this to define your own module.
        Every module receives the patient journey as parameter which is set to the instance variable of each module.
        This method should always save the result to the database, and return the id.
        """
        print(f"Starting Module {self.name}.")
        self.patient_journey = patient_journey
        self.patient_journey_sentences = patient_journey_sentences
        return 0
