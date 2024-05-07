"""Test cases for the extraction app."""
from django.test import TestCase
import pandas as pd

from extraction.logic.modules import (
    ActivityLabeler,
    TimeExtractor,
    EventTypeClassifier,
    LocationExtractor,
)


class ActivityLabelerTests(TestCase):
    """Test cases for the ActivityLabeler."""

    fixtures = ["tracex_project/extraction/fixtures/prompts_fixture.json"]

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

    fixtures = ["tracex_project/extraction/fixtures/prompts_fixture.json"]

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

    def test_return_value_is_datetime(self):
        """Tests if returned dataframe columns are of type datetime."""
        data = {"activity": ["fell ill"], "sentence_id": ["1"]}
        patient_journey = ["I fell ill on June 5 and recovered on June 7."]
        input_dataframe = pd.DataFrame(data)
        time_extractor = TimeExtractor()
        result = time_extractor.execute(
            df=input_dataframe, patient_journey_sentences=patient_journey
        )

        self.assertTrue((result["time:timestamp"].apply(lambda x: isinstance(x, pd.Timestamp))).all())
        self.assertTrue((result["time:end_timestamp"].apply(lambda x: isinstance(x, pd.Timestamp))).all())

    def test_processing_downwards(self):
        """Tests if the post-processing function is correctly applied to the dataframe downwards."""
        data = {"activity": ["fell ill", "had fever"], "sentence_id": ["1", "2"]}
        patient_journey = ["I fell ill on June 5 and recovered on June 7. After that I had fever."]
        input_dataframe = pd.DataFrame(data)
        time_extractor = TimeExtractor()
        result = time_extractor.execute(
            df=input_dataframe, patient_journey_sentences=patient_journey
        )

        self.assertTrue((result["time:timestamp"].apply(lambda x: isinstance(x, pd.Timestamp))).all())
        self.assertTrue((result["time:end_timestamp"].apply(lambda x: isinstance(x, pd.Timestamp))).all())

    def test_post_processing_upwards(self):
        """Tests if the post-processing function is correctly applied to the dataframe upwards."""
        data = {"activity": ["had fever", "fell ill",], "sentence_id": ["1", "2"]}
        patient_journey = ["I had fever. After that I fell ill on June 5 and recovered on June 7."]
        input_dataframe = pd.DataFrame(data)
        time_extractor = TimeExtractor()
        result = time_extractor.execute(
            df=input_dataframe, patient_journey_sentences=patient_journey
        )

        self.assertTrue((result["time:timestamp"].apply(lambda x: isinstance(x, pd.Timestamp))).all())
        self.assertTrue((result["time:end_timestamp"].apply(lambda x: isinstance(x, pd.Timestamp))).all())


class EventTypeClassifierTests(TestCase):
    """Test cases for the EventTypeClassifier."""

    fixtures = ["tracex_project/extraction/fixtures/prompts_fixture.json"]

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

    fixtures = ["tracex_project/extraction/fixtures/prompts_fixture.json"]

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
