"""Test cases for the extraction app."""

from django.test import TestCase
from tracex.extraction.logic.orchestrator import Orchestrator


class OrchestratorTests(TestCase):
    def test_single_instance_creation(self):
        orchestrator1 = Orchestrator()
        orchestrator2 = Orchestrator()
        self.assertIs(orchestrator1, orchestrator2)

    def test_consistent_object_state(self):
        orchestrator1 = Orchestrator()
        orchestrator2 = Orchestrator()

        orchestrator1.data = 'test_data'

        self.assertEqual(orchestrator1.data, orchestrator2.data)

    def test_get_instance_method(self):
        orchestrator1 = Orchestrator.get_instance()
        orchestrator2 = Orchestrator.get_instance()

        self.assertIs(orchestrator1, orchestrator2)

        orchestrator3 = Orchestrator()
        self.assertIs(orchestrator1, orchestrator3)
