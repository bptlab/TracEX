from dataclasses import dataclass

from .modules.module_patient_journey_generator import PatientJourneyGenerator
from .modules.module_activity_labeler import ActivityLabeler
from .modules.module_time_extractor import TimeExtractor
from .modules.module_location_extractor import LocationExtractor


@dataclass
class Configuration:
    path_patient_journey: str
    activity_key: str
    event_types: list
    locations: list

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


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
            "patient_journey_generation": PatientJourneyGenerator(
                name="Patient Journey Generator",
                description="Generates a patient journey with the help of the GPT engine.",
            ),
            # "pre_processing": modules.PreProcessor(),
            "activity_labeling": ActivityLabeler(
                name="Activity Labeler",
                description="Extracts the activity labels from a patient journey.",
            ),
            "time_extraction": TimeExtractor(
                name="Time Extractor",
                description="Extracts the timestamps for the corresponding activity labels from a patient journey.",
            ),
            "location_extraction": LocationExtractor(
                name="Location Extractor",
                description="Extracts the locations for the corresponding activity labels from a patient journey.",
            ),
            # "event_type_classification": modules.EventTypeClassifier(),
            # "visualization": modules.Visualizer(),
        }
        self.data = None

    @classmethod
    def get_instance(cls):
        """Return the singleton instance of the orchestrator."""
        return cls._instance

    def initilize_modules(self):
        pass

    def build_configuration(self, configuration: Configuration):
        self.configuration = configuration
        """ "
        1. Anforderungen in die richtige Reihenfolge bringen
        2. Module anhand der Anforderungen auswählen
        3. Module initialisieren
        """
        pass

    def testing(self):
        print("Test successful")
