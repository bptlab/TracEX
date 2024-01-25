from abc import ABC, abstractmethod
from pathlib import Path

from .logging import log_execution_time


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
        self.result = None

    @log_execution_time(Path("extraction/execution_time.log"))
    @abstractmethod
    def execute(self, _input, patient_journey=None):
        """
        Executes the logic of the module. Override this to define your own module.
        Every module receives the patient journey as parameter which is set to the instance variable of each module.
        This method should always save a dataframe in the "result" instance variable for internal processing.
        """
        print(f"Starting Module {self.name}.")
        self.patient_journey = patient_journey
