"""Module providing the orchestrator and corresponding configuration, that manages the modules."""
from dataclasses import dataclass
from typing import Optional, List, Dict
from django.utils.dateparse import parse_duration
from django.core.exceptions import ObjectDoesNotExist

from tracex.logic import utils

from .modules.module_activity_labeler import ActivityLabeler
from .modules.module_cohort_tagger import CohortTagger
from .modules.module_time_extractor_backup import TimeExtractorBackup
from .modules.module_location_extractor import LocationExtractor
from .modules.module_event_type_classifier import EventTypeClassifier

# from .modules.module_metrics_analyzer import MetricsAnalyzer
# from .modules.module_event_log_comparator import EventLogComparator

from ..models import Trace, PatientJourney, Event, Cohort


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
        "activity_labeling": ActivityLabeler,
        "cohort_tagging": CohortTagger,
        "event_type_classification": EventTypeClassifier,
        "time_extraction": TimeExtractorBackup,
        "location_extraction": LocationExtractor,
        # This module should be activated only if the user wants to analyze the metrics
        # "metrics_analyzer": MetricsAnalyzer,
        # Only activate this module with a test comparison patient journey as ground truth
        # "event_log_comparator": EventLogComparator,
    }
    activity_key: Optional[str] = "event_type"

    def update(self, **kwargs):
        """Update the configuration with a dictionary."""
        valid_keys = set(vars(self).keys())
        for key, value in kwargs.items():
            if key in valid_keys:
                setattr(self, key, value)
            else:
                print(f"Ignoring unknown key: {key}")


class Orchestrator:
    """Singleton class for managing the modules."""

    _instance = None

    def __new__(cls, configuration: ExtractionConfiguration = None):
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, configuration=None):
        if configuration is not None:
            self.configuration = configuration
        self.data = None
        self.db_objects: Dict[str, int] = {}

    @classmethod
    def get_instance(cls):
        """Return the singleton instance of the orchestrator."""
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance of the orchestrator."""
        cls._instance = None

    def set_configuration(self, configuration: ExtractionConfiguration):
        """Set the configuration for the orchestrator instance."""
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
            # This module should be activated only if the user wants to analyze the metrics
            # self.configuration.modules["metrics_analyzer"](),
            # Only activate this module with a test comparison patient journey as ground truth
            # self.configuration.modules["event_log_comparator"](),
        ]
        print("Initialization of modules successful.")
        return modules

    def run(self):
        """Run the modules."""
        modules = self.initialize_modules()
        self.db_objects["cohort"] = self.configuration.modules[
            "cohort_tagging"
        ]().execute_and_save(self.data, self.configuration.patient_journey)
        for module in modules:
            self.data = module.execute(self.data, self.configuration.patient_journey)
        if self.data is not None:
            try:
                latest_id = Trace.manager.latest("last_modified").id
            except ObjectDoesNotExist:
                latest_id = 0
            self.data.insert(0, "case_id", latest_id + 1)
            self.data.to_csv(utils.CSV_OUTPUT, index=False, header=True)

    # This method may be deleted later. The original idea was to always call Orchestrator.run() and depending on if
    # a configuration was given or not, the patient journey generation may be executed.
    def generate_patient_journey(self):
        """Generate a patient journey with the help of the GPT engine."""
        print("Orchestrator is generating a patient journey.")
        self.set_configuration(ExtractionConfiguration())
        module = self.configuration.modules["patient_journey_generation"]()
        patient_journey = module.execute(self.data, self.configuration.patient_journey)
        self.configuration.update(patient_journey=patient_journey)

    def save_results_to_db(self):
        """Save the trace to the database."""
        patient_journey: PatientJourney = PatientJourney.manager.get(
            pk=self.db_objects["patient_journey"]
        )
        trace: Trace = Trace.manager.create(patient_journey=patient_journey)
        events: List[Event] = Event.manager.bulk_create(
            [
                Event(
                    trace=trace,
                    activity=row["activity"],
                    event_type=row["event_type"],
                    start=row["start"],
                    end=row["end"],
                    duration=parse_duration(row["duration"]),
                    location=row["attribute_location"],
                )
                for _, row in self.data.iterrows()
            ]
        )
        trace.events.set(events)
        if self.db_objects["cohort"] and self.db_objects["cohort"] != 0:
            trace.cohort = Cohort.manager.get(pk=self.db_objects["cohort"])
        trace.save()
        patient_journey.trace.add(trace)
        patient_journey.save()
