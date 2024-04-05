"""Test cases for the extraction app."""
from unittest.mock import MagicMock
from django.test import TestCase
import pandas as pd

from extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration
from extraction.logic.modules.module_activity_labeler import ActivityLabeler
from extraction.logic.modules.module_time_extractor import TimeExtractor
from extraction.logic.modules.module_event_type_classifier import EventTypeClassifier
from extraction.logic.modules.module_location_extractor import LocationExtractor


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

        orchestrator1.data = 'test_data'

        self.assertEqual(orchestrator1.data, orchestrator2.data)

    def test_get_instance_method(self):
        """Tests if the get_instance method returns the same instance and if a new instance is the same instance."""
        Orchestrator.reset_instance()
        Orchestrator()
        orchestrator1 = Orchestrator.get_instance()
        orchestrator2 = Orchestrator.get_instance()

        self.assertIs(orchestrator1, orchestrator2)

        orchestrator3 = Orchestrator()
        self.assertIs(orchestrator1, orchestrator3)

    def test_reset_instance(self):
        """Tests if reset_instance resets the instance for all objects."""
        Orchestrator.reset_instance()
        orchestrator1 = Orchestrator()
        Orchestrator.reset_instance()
        orchestrator2 = Orchestrator
        self.assertIsNot(orchestrator1, orchestrator2)

    def test_set_configuration(self):
        """Tests if the set_configuration method correctly updates the Orchestrators instance's configuration."""
        Orchestrator.reset_instance()
        config = ExtractionConfiguration()
        orchestrator = Orchestrator(config)
        new_config = ExtractionConfiguration
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

    # Does not work yet, need to adjust initialization of modules
    def test_initialize_modules(self):
        """Tests if initialize_modules correctly initializes all modules."""
        Orchestrator.reset_instance()
        config = MagicMock()

        activity_labeling_mock = MagicMock()
        activity_labeling_mock.name = "activity_labeling"
        time_extraction_mock = MagicMock()
        time_extraction_mock.name = "time_extraction"
        event_type_classification_mock = MagicMock()
        event_type_classification_mock.name = "event_type_classification"
        location_extraction_mock = MagicMock()
        location_extraction_mock.name = "location_extraction"

        config.modules = {
            "activity_labeling": MagicMock(return_value=activity_labeling_mock),
            "time_extraction": MagicMock(return_value=time_extraction_mock),
            "event_type_classification": MagicMock(return_value=event_type_classification_mock),
            "location_extraction": MagicMock(return_value=location_extraction_mock),
        }

        orchestrator = Orchestrator(config)
        modules = orchestrator.initialize_modules()

        self.assertEqual(len(modules), 4)
        self.assertEqual(modules[0].name, "activity_labeling")
        self.assertEqual(modules[1].name, "time_extraction")
        self.assertEqual(modules[2].name, "event_type_classification")
        self.assertEqual(modules[3].name, "location_extraction")


class ActivityLabelerTests(TestCase):
    """Test cases for the ActivityLabeler."""

    def test_execute_return_value(self):
        """Tests if the return value of the execute method always is a dataframe and if column name is as expected."""
        input_dataframe = pd.DataFrame()
        test_data = "I fell ill yesterday."
        activity_labeler = ActivityLabeler()
        result = activity_labeler.execute(_input=input_dataframe, patient_journey=test_data)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("activity", result.columns)


class TimeExtractorTests(TestCase):
    """Test cases for the TimeExtractor."""

    def test_execute_return_value(self):
        """Tests if the return value of the execute method is always a dataframe and if column names are as expected."""
        input_dataframe = pd.DataFrame(["fell ill"], columns=["activity"])
        test_data = "I fell ill on June 1 and recovered on June 5."
        time_extractor = TimeExtractor()
        result = time_extractor.execute(df=input_dataframe, patient_journey=test_data)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("start", result.columns)
        self.assertIn("end", result.columns)
        self.assertIn("duration", result.columns)


class EventTypeClassifierTests(TestCase):
    """Test cases for the EventTypeClassifier."""

    def test_execute_return_value(self):
        """Tests if the return value of the execute method is always a dataframe and if column name is as expected."""
        test_data = {
            "activity": "fell ill",
            "start": "20220601T0000",
            "end": "20220605T0000",
            "duration": "04:00:00",
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
            "start": "20220601T0000",
            "end": "20220605T0000",
            "duration": "04:00:00",
            "event_type": "Symptom Onset",
        }
        input_dataframe = pd.DataFrame([test_data])
        location_extractor = LocationExtractor()
        result = location_extractor.execute(input_dataframe)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("attribute_location", result.columns)