import csv
from dataclasses import dataclass

import pandas as pd
import pm4py

from .modules.module_patient_journey_generator import PatientJourneyGenerator
from .modules.module_activity_labeler import ActivityLabeler
from .modules.module_time_extractor import TimeExtractor
from .modules.module_location_extractor import LocationExtractor
from .modules.module_event_type_classifier import EventTypeClassifier

from ..logic import utils


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
        self.modules = {
            "patient_journey_generation": PatientJourneyGenerator,
            "activity_labeling": ActivityLabeler,
            "time_extraction": TimeExtractor,
            "location_extraction": LocationExtractor,
            "event_type_classification": EventTypeClassifier,
        }
        self.data = None

    @classmethod
    def get_instance(cls):
        """Return the singleton instance of the orchestrator."""
        return cls._instance

    def set_configuration(self, configuration: utils.ExtractionConfiguration):
        self.configuration = configuration

    def initialize_modules(self):
        """Bring the modules into the right order and initialize them."""
        # Make changes here, if selection and reordering of modules should be more sofisticated
        # (i.e. depending on config given by user)
        modules = [
            self.modules["activity_labeling"](),
            self.modules["time_extraction"](),
            self.modules["event_type_classification"](),
            self.modules["location_extraction"](),
        ]

        return modules

    def run(self):
        """Run the modules."""
        modules = self.initialize_modules()
        for module in modules:
            module.execute(self.data, self.configuration.patient_journey)
            self.data = module.result
        return self.__convert_bulletpoints_to_csv(self.data)

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
