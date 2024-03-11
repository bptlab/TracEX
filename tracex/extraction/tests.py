"""Test cases for the extraction app."""
from unittest.mock import MagicMock
from django.test import TestCase

from tracex.extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration


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
