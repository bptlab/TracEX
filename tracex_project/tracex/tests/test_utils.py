"""Test cases for utils."""
from django.test import TestCase
import pandas as pd

from tracex.logic.utils import Conversion, DataFrameUtilities


class ConversionTests(TestCase):
    """Test cases for the conversion class inside the utils module."""
    def test_prepare_df_for_xes_conversion(self):
        """Tests if the dataframe contains the correct column name for xes conversion"""
        data = {
            "case:concept:name": [1, 1],
            "activity": ["fell ill", "went to the doctor"],
            "time:timestamp": ["2021-06-05", "2021-06-06"],
            "event_type": ["Symptom Onset", "Doctor Visit"],
        }
        df = pd.DataFrame(data)
        activity_key = "event_type"
        df_renamed = Conversion.prepare_df_for_xes_conversion(
            df, activity_key=activity_key
        )

        self.assertIn("case:concept:name", df_renamed.columns)
        self.assertIsInstance(df_renamed["time:timestamp"][0], str)

    def test_rename_columns(self):
        """Tests if the columns are correctly renamed before displaying them."""
        data = {
            "case:concept:name": [1, 1],
            "activity": ["fell ill", "went to the doctor"],
            "event_type": ["Symptom Onset", "Doctor Visit"],
            "time:timestamp": ["2021-06-05", "2021-06-06"],
            "time:end_timestamp": ["2021-06-05", "2021-06-06"],
            "time:duration": ["24:00:00", "24:00:00"],
            "attribute_location": ["Home", "Doctors"],
            "activity_relevance": ["High", "High"],
            "timestamp_correctness": ["True", "True"],
            "correctness_confidence": [0.95, 0.96],
        }
        df = pd.DataFrame(data)
        df_renamed = Conversion.rename_columns(df)

        self.assertIn("Case ID", df_renamed.columns)
        self.assertIn("Activity", df_renamed.columns)
        self.assertIn("Event Type", df_renamed.columns)
        self.assertIn("Start Timestamp", df_renamed.columns)
        self.assertIn("End Timestamp", df_renamed.columns)
        self.assertIn("Duration", df_renamed.columns)
        self.assertIn("Location", df_renamed.columns)

    def test_html_table_from_df(self):
        """Tests if the html table is correctly created from the dataframe."""
        data = {
            "case:concept:name": [1, 1],
            "activity": ["fell ill", "went to the doctor"],
            "time:timestamp": ["2021-06-05", "2021-06-06"],
        }
        df = pd.DataFrame(data)
        html_table = Conversion.create_html_table_from_df(df)

        self.assertIn("<table>", html_table)




class DataframeUtilitiesTests(TestCase):
    """Test cases for the dataframe utilities inside the utils module."""

