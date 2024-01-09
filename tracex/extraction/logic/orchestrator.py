from .modules.module_patient_journey_generator import PatientJourneyGenerator


class Orchestrator:
    def __init__(self, config):
        print("test")
        self.config = config
        self.modules = {
            "patient_journey_generation": PatientJourneyGenerator(
                name="Patient Journey Generator",
                description="Generates a patient journey with the help of the GPT engine.",
            ),
            # "pre_processing": modules.PreProcessor(),
            # "activity_labeling": modules.ActivityLabeler(),
            # "time_extraction": modules.TimeExtractor(),
            # "location_extraction": modules.LocationExtractor(),
            # "event_type_classification": modules.EventTypeClassifier(),
            # "visualization": modules.Visualizer(),
        }
        self.data = None

    def initilize_modules(self):
        pass

    def built_configuration(self, anforderungen):
        """ "
        1. Anforderungen in die richtige Reihenfolge bringen
        2. Module anhand der Anforderungen auswählen
        3. Module initialisieren
        """
        pass
