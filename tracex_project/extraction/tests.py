"""Test cases for the extraction app."""
from django.test import TestCase
import pandas as pd

from extraction.logic.orchestrator import ExtractionConfiguration, Orchestrator
from extraction.logic.modules import (
    ActivityLabeler,
    TimeExtractor,
    EventTypeClassifier,
    LocationExtractor,
)


class OrchestratorTests(TestCase):
    """Test cases for the Orchestrator class utilizing the ExtractionConfiguration."""

    def test_single_instance_creation(self):
        """Tests if two initialized orchestrators are the same instance."""
        Orchestrator.reset_instance()
        orchestrator1 = Orchestrator()
        orchestrator2 = Orchestrator()

        self.assertIs(orchestrator1, orchestrator2)

    def test_consistent_object_state(self):
        """Tests if the state of the orchestrator instance is the same for two instances."""
        Orchestrator.reset_instance()
        orchestrator1 = Orchestrator()
        orchestrator2 = Orchestrator()
        orchestrator1.data = "test_data"

        self.assertEqual(orchestrator1.data, orchestrator2.data)

    def test_get_instance_method(self):
        """Tests if the get_instance method returns the same instance and if a new instance is the same instance."""
        Orchestrator.reset_instance()
        Orchestrator()
        orchestrator1 = Orchestrator.get_instance()
        orchestrator2 = Orchestrator.get_instance()
        orchestrator3 = Orchestrator()

        self.assertIs(orchestrator1, orchestrator2)
        self.assertIs(orchestrator1, orchestrator3)

    def test_reset_instance(self):
        """Tests if reset_instance resets the instance for all objects."""
        Orchestrator.reset_instance()
        orchestrator1 = Orchestrator()
        Orchestrator.reset_instance()
        orchestrator2 = Orchestrator()

        self.assertIsNot(orchestrator1, orchestrator2)

    def test_set_configuration(self):
        """Tests if the set_configuration method correctly updates the Orchestrators instance's configuration."""
        Orchestrator.reset_instance()
        config = ExtractionConfiguration()
        orchestrator = Orchestrator(config)
        new_config = ExtractionConfiguration()
        orchestrator.set_configuration(new_config)

        self.assertIs(orchestrator.configuration, new_config)

    def test_singleton_with_configuration(self):
        """Tests that the Orchestrator's configuration remains unchanged with subsequent instantiations."""
        Orchestrator.reset_instance()
        config1 = ExtractionConfiguration()
        orchestrator1 = Orchestrator(config1)
        config2 = ExtractionConfiguration()
        orchestrator2 = Orchestrator(config2)

        self.assertIs(orchestrator1.configuration, orchestrator2.configuration)

    def test_initialize_modules(self):
        """Tests if initialize_modules correctly initializes a module."""
        Orchestrator.reset_instance()
        config = ExtractionConfiguration()
        orchestrator = Orchestrator(configuration=config)
        orchestrator.configuration.update(
            modules={
                "activity_labeling": ActivityLabeler,
            }
        )
        modules = orchestrator.initialize_modules()

        self.assertTrue(any(isinstance(module, ActivityLabeler) for module in modules))
        self.assertEqual(modules[0].name, "Activity Labeler")


class ActivityLabelerTests(TestCase):
    """Test cases for the ActivityLabeler."""

    def test_execute_return_value(self):
        """Tests if the return value of the execute method always is a dataframe and if column name is as expected."""
        test_data = ["I fell ill yesterday.", "I went to the doctor today."]
        activity_labeler = ActivityLabeler()
        result = activity_labeler.execute(patient_journey_sentences=test_data)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("activity", result.columns)
        self.assertIn("sentence_id", result.columns)


class TimeExtractorTests(TestCase):
    """Test cases for the TimeExtractor."""

    def test_execute_return_value(self):
        """Tests if the return value of the execute method is always a dataframe and if column names are as expected."""
        data = {"activity": ["fell ill"], "sentence_id": ["1"]}
        patient_journey = ["I fell ill on June 5 and recovered on June 7."]
        input_dataframe = pd.DataFrame(data)
        time_extractor = TimeExtractor()
        result = time_extractor.execute(
            df=input_dataframe, patient_journey_sentences=patient_journey
        )

        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("time:timestamp", result.columns)
        self.assertIn("time:end_timestamp", result.columns)
        self.assertIn("time:duration", result.columns)


class EventTypeClassifierTests(TestCase):
    """Test cases for the EventTypeClassifier."""

    def test_execute_return_value(self):
        """Tests if the return value of the execute method is always a dataframe and if column name is as expected."""
        test_data = {
            "activity": "fell ill",
            "time:timestamp": "20220601T0000",
            "time:end_timestamp": "20220605T0000",
            "time:duration": "96:00:00",
        }
        input_dataframe = pd.DataFrame([test_data])
        event_type_classifier = EventTypeClassifier()
        result = event_type_classifier.execute(input_dataframe)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("event_type", result.columns)


class LocationExtractorTests(TestCase):
    """Test cases for the LocationExtractor."""

    def test_execute_return_value(self):
        """Tests if the return value of the execute method is always a dataframe and if column name is as expected."""
        test_data = {
            "activity": "fell ill",
            "time:timestamp": "20220601T0000",
            "time:end_timestamp": "20220605T0000",
            "time:duration": "96:00:00",
            "event_type": "Symptom Onset",
        }
        input_dataframe = pd.DataFrame([test_data])
        location_extractor = LocationExtractor()
        result = location_extractor.execute(input_dataframe)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("attribute_location", result.columns)
