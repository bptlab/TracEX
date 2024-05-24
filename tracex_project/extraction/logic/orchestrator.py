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
from tracex.logic.utils import DataFrameUtilities


@dataclass
class ExtractionConfiguration:
    """
    Dataclass for the configuration of the orchestrator. This specifies all modules that can be executed, what event
    types are used to classify the activity labels, what locations are used to classify the activity labels and what the
    patient journey is, on which the pipeline is executed.
    """

    def __init__(
        self,
        patient_journey: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        activity_key: Optional[str] = "event_type",
    ):
        self.patient_journey = patient_journey
        self.event_types = event_types
        self.locations = locations
        self.activity_key = activity_key
        self.modules = {
            "preprocessing": Preprocessor,
            "cohort_tagging": CohortTagger,
            "activity_labeling": ActivityLabeler,
            "time_extraction": TimeExtractor,
            "event_type_classification": EventTypeClassifier,
            "location_extraction": LocationExtractor,
            "metrics_analyzer": MetricsAnalyzer,
        }

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
        self.cohort = None
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

    def set_cohort(self, cohort):
        """Set the cohort for the orchestrator instance."""
        self.cohort = cohort

    def get_cohort(self):
        """Return the cohort for the orchestrator instance."""
        return self.cohort

    def set_db_objects_id(self, object_name: str, object_id: int):
        """Set the database id objects for the orchestrator instance."""
        self.db_objects_id[object_name] = object_id

    def get_db_objects_id(self, object_name):
        """Return the database id objects for the orchestrator instance."""
        return self.db_objects_id[object_name]

    def update_modules(self, modules_list):
        """Update the modules of the orchestrator instance."""
        modules_dictionary = self.get_configuration().modules
        updated_modules = {
            key: modules_dictionary[key]
            for key in modules_dictionary
            if key in modules_list
        }
        self.get_configuration().update(modules=updated_modules)

    def initialize_modules(self):
        """Bring the modules into the right order and initialize them."""
        # Make changes here, if selection and reordering of modules should be more sophisticated
        # (i.e. depending on config given by user)
        modules = {
            key: self.get_configuration().modules[key]()
            for key in self.get_configuration().modules
        }
        print("Initialization of modules successful.")
        return modules

    def run(self, view=None):
        """Run the modules."""
        modules = self.initialize_modules()
        current_step = 1

        patient_journey_sentences = self.get_configuration().patient_journey.split(". ")
        if "preprocessing" in modules:
            self.update_progress(view, current_step, "Preprocessing")
            patient_journey_sentences = modules["preprocessing"].execute(
                patient_journey=self.get_configuration().patient_journey
            )
            current_step += 1
        patient_journey = ". ".join(patient_journey_sentences)

        if "cohort_tagging" in modules:
            self.update_progress(view, current_step, "Cohort Tagger")
            self.set_cohort(
                modules["cohort_tagging"].execute_and_save(
                    self.get_data(),
                    patient_journey=patient_journey,
                    patient_journey_sentences=patient_journey_sentences,
                )
            )
            current_step += 1

        for module_name in [
            name for name in modules if name not in ("cohort_tagging", "preprocessing")
        ]:
            module = modules[module_name]
            self.update_progress(view, current_step, module.name)
            self.set_data(
                module.execute(
                    self.get_data(),
                    patient_journey=patient_journey,
                    patient_journey_sentences=patient_journey_sentences,
                    cohort=self.get_cohort(),
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
            self.set_default_values()

    def save_results_to_db(self):
        """Save the trace to the database."""
        patient_journey: PatientJourney = PatientJourney.manager.get(
            pk=self.get_db_objects_id("patient_journey")
        )
        trace: Trace = Trace.manager.create(patient_journey=patient_journey)
        events_with_metric_list = []
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
            events_with_metric_list.append(event)
            metric_list.append(metric)

        events: List[Event] = Event.manager.bulk_create(events_with_metric_list)
        for event, metric in zip(events, metric_list):
            metric.event = event
        Metric.manager.bulk_create(metric_list)
        trace.events.set(events)

        Cohort.manager.create(trace=trace, **self.get_cohort())

        trace.save()
        patient_journey.trace.add(trace)
        patient_journey.save()

    def set_default_values(self):
        """Set default values if a specific module was deselected."""
        config_modules = self.get_configuration().modules
        data = self.get_data()

        if "time_extraction" not in config_modules:
            DataFrameUtilities.set_default_timestamps(data)
        if "event_type_classification" not in config_modules:
            data["event_type"] = "N/A"
        if "location_extraction" not in config_modules:
            data["attribute_location"] = "N/A"
        if "metrics_analyzer" not in config_modules:
            data["activity_relevance"] = None
            data["timestamp_correctness"] = None
            data["correctness_confidence"] = None
        if "cohort_tagging" not in config_modules:
            cohort_default_values = {
                "age": None,
                "sex": None,
                "origin": None,
                "condition": None,
                "preexisting_condition": None,
            }
            self.set_cohort(cohort_default_values)

    def update_progress(self, view, current_step, module_name):
        """Update the progress of the extraction."""
        if view is not None:
            percentage = round(
                (current_step / (len(self.get_configuration().modules) + 1)) * 100
            )
            view.request.session["progress"] = percentage
            view.request.session["status"] = module_name
            view.request.session.save()
