"""Test cases for the Orchestrator class."""
import pandas as pd
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory

from extraction.logic.orchestrator import ExtractionConfiguration, Orchestrator
from extraction.logic.modules import (
    Preprocessor,
    ActivityLabeler,
)


class MockConfiguration:
    """Mock configuration class for testing purposes."""
    modules = ["Preprocessor", "Cohort Tagger", "ActivityLabeler", "TimeExtractor", "EventTypeClassifier"]


class OrchestratorTests(TestCase):
    """Test cases for the Orchestrator class utilizing the ExtractionConfiguration."""

    fixtures = ["tracex_project/extraction/fixtures/prompts_fixture.json"]

    def setUp(self):  # pylint: disable=invalid-name
        """Set up method that gets called everytime before tests are executed."""
        self.factory = RequestFactory()
        self.orchestrator = Orchestrator()

        self.orchestrator.get_configuration = lambda: MockConfiguration()  # pylint: disable=unnecessary-lambda

    def tearDown(self):  # pylint: disable=invalid-name
        """Tear down method that gets called after every test is executed."""
        Orchestrator.reset_instance()

    def test_single_instance_creation(self):
        """Tests if two initialized orchestrators are the same instance."""
        orchestrator1 = Orchestrator()
        orchestrator2 = Orchestrator()

        self.assertIs(orchestrator1, orchestrator2)

    def test_consistent_object_state(self):
        """Tests if the state of the orchestrator instance is the same for two instances."""
        orchestrator1 = Orchestrator()
        orchestrator2 = Orchestrator()
        orchestrator1.data = "test_data"

        self.assertEqual(orchestrator1.data, orchestrator2.data)

    def test_get_instance_method(self):
        """Tests if the get_instance method returns the same instance and if a new instance is the same instance."""
        Orchestrator()
        orchestrator1 = Orchestrator.get_instance()
        orchestrator2 = Orchestrator.get_instance()
        orchestrator3 = Orchestrator()

        self.assertIs(orchestrator1, orchestrator2)
        self.assertIs(orchestrator1, orchestrator3)

    def test_reset_instance(self):
        """Tests if reset_instance resets the instance for all objects."""
        orchestrator1 = Orchestrator()
        Orchestrator.reset_instance()
        orchestrator2 = Orchestrator()

        self.assertIsNot(orchestrator1, orchestrator2)

    def test_set_configuration(self):
        """Tests if the set_configuration method correctly updates the Orchestrators instance's configuration."""
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

    def test_run(self):
        """Tests if the run method correctly return a dataframe. Execution of ActivityLabeler and Preprocessor is
        necessary since the run method makes assumptions on how the patient journey looks like."""
        Orchestrator.reset_instance()
        config = ExtractionConfiguration(
            patient_journey="This is a test patient journey. This is some description about how I fell and and "
                            "recovered in the end.",
        )
        config.update(
            modules={
                "preprocessing": Preprocessor,
                "activity_labeling": ActivityLabeler,
            }
        )
        orchestrator = Orchestrator(configuration=config)
        orchestrator.run()

        self.assertIsNot(orchestrator.get_data(), None)
        self.assertIsInstance(orchestrator.get_data(), pd.DataFrame)

    def test_set_db_objects_id(self):
        """Test if the set_db_objects_id method correctly sets the object ID."""
        object_name = "test_object"
        object_id = 123

        self.orchestrator.set_db_objects_id(object_name, object_id)

        self.assertEqual(self.orchestrator.db_objects_id[object_name], object_id)

    def test_get_db_objects_id(self):
        """Test if the get_db_objects_id method returns the correct object ID."""
        object_name = "test_object"
        object_id = 456

        self.orchestrator.set_db_objects_id(object_name, object_id)
        retrieved_id = self.orchestrator.get_db_objects_id(object_name)

        self.assertEqual(retrieved_id, object_id)

    def test_get_db_objects_id_key_error(self):
        """Test if the get_db_objects_id method raises a KeyError when the object name is not found."""
        object_name = "non_existent_object"

        with self.assertRaises(KeyError):
            self.orchestrator.get_db_objects_id(object_name)

    def test_update_progress_with_view(self):
        """Tests if the progress of the views are updated correctly."""
        request = self.factory.get("/extraction/filter")
        middleware = SessionMiddleware(lambda req: req)
        middleware.process_request(request)
        request.session.save()

        class MockView:
            """Mock View class for testing purposes."""
            def __init__(self, request):
                self.request = request

        view = MockView(request)
        current_step = 2
        module_name = "Activity Labeler"

        self.orchestrator.update_progress(view, current_step, module_name)

        self.assertEqual(request.session["progress"], 40)  # 2/5 = 0.4 * 100 = 40
        self.assertEqual(request.session["status"], module_name)

    def test_update_progress_without_view(self):
        """Tests if the progress of the views are updated correctly."""
        current_step = 2
        module_name = "Activity Labeler"

        self.orchestrator.update_progress(None, current_step, module_name)

        # No assertions needed since the method should just return without updating the session
