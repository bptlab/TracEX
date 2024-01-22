import csv
from dataclasses import dataclass
from typing import Optional, List

from . import Module
from .modules.module_patient_journey_generator import PatientJourneyGenerator
from .modules.module_activity_labeler import ActivityLabeler
from .modules.module_time_extractor import TimeExtractor
from .modules.module_location_extractor import LocationExtractor
from .modules.module_event_type_classifier import EventTypeClassifier

from ..logic import utils


@dataclass
class ExtractionConfiguration:
    """
    Dataclass for the configuration of the orchestrator. This specifies all modules that can be executed, what event
    types are used to classify the activity labels, what locations are used to classify the activity labels and what the
    patient journey is, on which the pipeline is executed.
    """

    patient_journey: Optional[str] = None
    event_types: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    modules = {
        "patient_journey_generation": PatientJourneyGenerator,
        "activity_labeling": ActivityLabeler,
        "time_extraction": TimeExtractor,
        "location_extraction": LocationExtractor,
        "event_type_classification": EventTypeClassifier,
    }
    activity_key: Optional[str] = "event_type"

    def update(self, **kwargs):
        """Update the configuration with a dictionary."""
        valid_keys = set(self.__annotations__.keys())
        for key, value in kwargs.items():
            if key in valid_keys:
                setattr(self, key, value)
            else:
                print(f"Ignoring unknown key: {key}")


class Orchestrator:
    """Singleton class for managing the modules."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self):
        self.configuration = None
        self.data = None

    @classmethod
    def get_instance(cls):
        """Return the singleton instance of the orchestrator."""
        return cls._instance

    def set_configuration(self, configuration: ExtractionConfiguration):
        self.configuration = configuration

    def initialize_modules(self):
        """Bring the modules into the right order and initialize them."""
        # Make changes here, if selection and reordering of modules should be more sophisticated
        # (i.e. depending on config given by user)
        modules = [
            self.configuration.modules["activity_labeling"](),
            self.configuration.modules["time_extraction"](),
            self.configuration.modules["event_type_classification"](),
            self.configuration.modules["location_extraction"](),
        ]
        print("Initialization of modules successful.")
        return modules

    def run(self):
        """Run the modules."""
        modules = self.initialize_modules()
        for module in modules:
            module.execute(self.data, self.configuration.patient_journey)
            self.data = module.result
            # if self.data is not None:
            #     self.data.merge(module.result, how="inner", on="event_information", validate="one_to_one")
            # else:
            #     self.data = module.result
        # replace with self.data = self.__convert_bulletpoints_to_csv(self.data) when dataframes are implemented
        return self.__convert_bulletpoints_to_csv(self.data)

    # This method may be deleted later. The original idea was to always call Orchestrator.run() and depending on if
    # a configuration was given or not, the patient journey generation may be executed.
    def generate_patient_journey(self):
        """Generate a patient journey with the help of the GPT engine."""
        print("Orchestrator is generating a patient journey.")
        module = self.configuration.modules["patient_journey_generation"]()
        module.execute(self.data, self.configuration.patient_journey)
        self.configuration.update(patient_journey=module.result)

    # Will be deleted when dataframes are implemented
    @staticmethod
    def __convert_bulletpoints_to_csv(bulletpoints_start_end):
        """Converts the bulletpoints to a CSV file."""
        bulletpoints_list = bulletpoints_start_end.split("\n")
        bulletpoints_matrix = []
        for entry in bulletpoints_list:
            entry = entry.strip("- ")
            entry = entry.split(", ")
            bulletpoints_matrix.append(entry)
        fields = [
            "caseID",
            "event_information",
            "start",
            "end",
            "duration",
            "event_type",
            "attribute_location",
        ]
        for row in bulletpoints_matrix:
            row.insert(0, 1)
        outputfile = utils.CSV_OUTPUT
        with open(outputfile, "w") as f:
            write = csv.writer(f)
            write.writerow(fields)
            write.writerows(bulletpoints_matrix)
        return outputfile
