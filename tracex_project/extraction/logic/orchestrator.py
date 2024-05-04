"""Module providing the orchestrator and corresponding configuration, that manages the modules."""
from dataclasses import dataclass
from typing import Optional, List, Dict
from django.utils.dateparse import parse_duration
from django.core.exceptions import ObjectDoesNotExist

from extraction.logic.modules import (
    Preprocessor,
    CohortTagger,
    ActivityLabeler,
    TimeExtractor,
    EventTypeClassifier,
    LocationExtractor,
    MetricsAnalyzer,
)
from extraction.models import Trace, PatientJourney, Event, Cohort, Metric


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
        "preprocessing": Preprocessor,
        "cohort_tagging": CohortTagger,
        "activity_labeling": ActivityLabeler,
        "time_extraction": TimeExtractor,
        "event_type_classification": EventTypeClassifier,
        "location_extraction": LocationExtractor,
        "metrics_analyzer": MetricsAnalyzer,
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
        self.db_objects_id: Dict[str, int] = {}

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

    def get_configuration(self):
        """Return the configuration for the orchestrator instance."""
        return self.configuration

    def set_data(self, data):
        """Set the data for the orchestrator instance."""
        self.data = data

    def get_data(self):
        """Return the data for the orchestrator instance."""
        return self.data

    def set_db_objects_id(self, object_name: str, object_id: int):
        """Set the database id objects for the orchestrator instance."""
        self.db_objects_id[object_name] = object_id

    def get_db_objects_id(self, object_name):
        """Return the database id objects for the orchestrator instance."""
        return self.db_objects_id[object_name]

    def initialize_modules(self):
        """Bring the modules into the right order and initialize them."""
        # Make changes here, if selection and reordering of modules should be more sophisticated
        # (i.e. depending on config given by user)
        modules = [
            self.get_configuration().modules["activity_labeling"](),
            self.get_configuration().modules["time_extraction"](),
            self.get_configuration().modules["event_type_classification"](),
            self.get_configuration().modules["location_extraction"](),
            self.get_configuration().modules["metrics_analyzer"](),
        ]
        print("Initialization of modules successful.")
        return modules

    def run(self, view=None):
        """Run the modules."""
        modules = self.initialize_modules()
        current_step = 0

        patient_journey_sentences = self.get_configuration().patient_journey.split(". ")
        if "preprocessing" in self.get_configuration().modules:
            preprocessor = self.get_configuration().modules.get("preprocessing")()
            self.update_progress(view, current_step, "Preprocessing")
            patient_journey_sentences = preprocessor.execute(
                patient_journey=self.get_configuration().patient_journey
            )
            current_step += 1
        patient_journey = ". ".join(patient_journey_sentences)

        self.update_progress(view, current_step, "Cohort Tagger")
        self.db_objects_id["cohort"] = (
            self.get_configuration()
            .modules["cohort_tagging"]()
            .execute_and_save(
                self.get_data(),
                patient_journey=patient_journey,
                patient_journey_sentences=patient_journey_sentences,
            )
        )
        current_step += 1
        for module in modules:
            self.update_progress(view, current_step, module.name)
            self.set_data(
                module.execute(
                    self.get_data(),
                    patient_journey=patient_journey,
                    patient_journey_sentences=patient_journey_sentences,
                )
            )
            current_step += 1

        if self.get_data() is not None:
            try:
                latest_id = Trace.manager.latest("last_modified").id
            except ObjectDoesNotExist:
                latest_id = 0
            del self.get_data()["sentence_id"]
            self.get_data().insert(0, "case:concept:name", latest_id + 1)

    def save_results_to_db(self):
        """Save the trace to the database."""
        patient_journey: PatientJourney = PatientJourney.manager.get(
            pk=self.db_objects_id["patient_journey"]
        )
        trace: Trace = Trace.manager.create(patient_journey=patient_journey)
        events_with_metric = []
        metric_list = []
        for _, row in self.get_data().iterrows():
            event = Event(
                trace=trace,
                activity=row["activity"],
                event_type=row["event_type"],
                start=row["time:timestamp"],
                end=row["time:end_timestamp"],
                duration=parse_duration(row["time:duration"]),
                location=row["attribute_location"],
            )
            metric = Metric(
                activity_relevance=row["activity_relevance"],
                timestamp_correctness=row["timestamp_correctness"],
                correctness_confidence=row["correctness_confidence"],
            )
            event.metric = metric
            events_with_metric.append(event)
            metric_list.append(metric)

        events: List[Event] = Event.manager.bulk_create(events_with_metric)
        for event, metric in zip(events, metric_list):
            metric.event = event
        Metric.manager.bulk_create(metric_list)
        trace.events.set(events)
        if self.db_objects_id["cohort"] and self.db_objects_id["cohort"] != 0:
            trace.cohort = Cohort.manager.get(pk=self.db_objects_id["cohort"])
        trace.save()
        patient_journey.trace.add(trace)
        patient_journey.save()

    def update_progress(self, view, current_step, module_name):
        """Update the progress of the extraction."""
        if view is not None:
            percentage = round(
                (current_step / len(self.get_configuration().modules)) * 100
            )
            view.request.session["progress"] = percentage
            view.request.session["status"] = module_name
            view.request.session.save()
