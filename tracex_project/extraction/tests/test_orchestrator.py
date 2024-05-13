"""Test cases for the Orchestrator class."""
from django.test import TestCase

from extraction.logic.orchestrator import ExtractionConfiguration, Orchestrator
from extraction.logic.modules import ActivityLabeler


class OrchestratorTests(TestCase):
    """Test cases for the Orchestrator class utilizing the ExtractionConfiguration."""

    fixtures = ["tracex_project/extraction/fixtures/prompts_fixture.json"]

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

        self.assertIsInstance(modules['activity_labeling'], ActivityLabeler)
        self.assertEqual(modules['activity_labeling'].name, "Activity Labeler")
