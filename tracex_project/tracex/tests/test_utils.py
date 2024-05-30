"""Test cases for utils."""
from django.db.models import Q
from django.test import TestCase
import pandas as pd

from extraction.models import Trace
from tracex.logic.utils import Conversion, DataFrameUtilities


class ConversionTests(TestCase):
    """Test cases for the conversion class inside the utils module."""

    def test_prepare_df_for_xes_conversion(self):
        """Test if the DataFrame contains the correct column name for XES conversion"""
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
        """Test if the columns are correctly renamed before displaying them."""
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

    def test_create_html_table_from_df(self):
        """Test if the HTML table is correctly created from the DataFrame."""
        data = {
            "case:concept:name": [1, 1],
            "activity": ["fell ill", "went to the doctor"],
            "time:timestamp": ["2021-06-05", "2021-06-06"],
        }
        df = pd.DataFrame(data)
        html_table = Conversion.create_html_table_from_df(df)

        self.assertIn("<table", html_table)

    def test_create_dfg_from_df(self):
        """Test if the directly-follows-graph image is correctly created from the DataFrame."""
        data = {
            "case:concept:name": [1, 1],
            "activity": ["fell ill", "went to the doctor"],
            "time:timestamp": ["20210605T0000", "20210606T0000"],
            "event_type": ["Symptom Onset", "Doctor Visit"],
        }
        df = pd.DataFrame(data)
        df["time:timestamp"] = pd.to_datetime(
            df["time:timestamp"], format="%Y%m%dT%H%M", errors="coerce"
        )
        dfg_img = Conversion.create_dfg_from_df(df, "event_type")

        self.assertIsNot(None, dfg_img)

    def test_dataframe_to_xes(self):
        """Test if the DataFrame is converted to XES under the right filepath."""
        data = {
            "case:concept:name": [1, 1],
            "activity": ["fell ill", "went to the doctor"],
            "time:timestamp": ["2021-06-05", "2021-06-06"],
            "event_type": ["Symptom Onset", "Doctor Visit"],
        }
        df = pd.DataFrame(data)
        file_path = Conversion.dataframe_to_xes(df, "test", "event_type")
        with open(file_path, "r") as file:
            file_content = file.read()

        self.assertIn("test.xes", file_path)
        self.assertIn('<?xml version="1.0" encoding="utf-8" ?>', file_content)
        self.assertIn("<log", file_content)


class DataframeUtilitiesTests(TestCase):
    """Test cases for the DataFrame utilities inside the utils module."""

    fixtures = ["tracex_project/tracex/fixtures/dataframe_fixtures.json"]

    def test_get_events_df(self):
        """Test if get_events_df returns all events in a dataframe correctly."""
        events_df = DataFrameUtilities.get_events_df()

        self.assertIsInstance(events_df, pd.DataFrame)
        self.assertIn("case:concept:name", events_df.columns)
        self.assertIn("activity", events_df.columns)
        self.assertIn("time:timestamp", events_df.columns)
        self.assertIn("time:end_timestamp", events_df.columns)
        self.assertIn("event_type", events_df.columns)
        self.assertIn("attribute_location", events_df.columns)

    def test_get_events_df_with_query(self):
        """Test if get_events_df returns queried events in a DataFrame correctly."""
        query_last_trace = Q(
            id=Trace.manager.filter().latest("last_modified").id
        )
        events_df = DataFrameUtilities.get_events_df(query=query_last_trace)

        self.assertIsInstance(events_df, pd.DataFrame)
        self.assertIn("case:concept:name", events_df.columns)
        self.assertIn("activity", events_df.columns)
        self.assertIn("time:timestamp", events_df.columns)
        self.assertIn("time:end_timestamp", events_df.columns)
        self.assertIn("event_type", events_df.columns)
        self.assertIn("attribute_location", events_df.columns)

    def test_filter_dataframe(self):
        """Test if the DataFrame is correctly filtered."""
        data = {
            "case:concept:name": [1, 1],
            "activity": ["fell ill", "went to the doctor"],
            "time:timestamp": ["2021-06-05", "2021-06-06"],
            "event_type": ["Symptom Onset", "Doctor Visit"],
        }
        df = pd.DataFrame(data)
        filter_dict = {
            "event_type": ["Symptom Onset"],
        }
        filtered_df = DataFrameUtilities.filter_dataframe(df, filter_dict)

        self.assertIn("Symptom Onset", filtered_df["event_type"].values)
        self.assertNotIn("Doctor Visit", filtered_df["event_type"].values)

    def test_set_default_timestamps(self):
        """Test if default timestamps are set correctly"""
        data = {
            "case:concept:name": [1, 1],
            "activity": ["fell ill", "went to the doctor"],
            "time:timestamp": ["N/A", "N/A"],
        }
        df = pd.DataFrame(data)
        DataFrameUtilities.set_default_timestamps(df)

        self.assertNotIn("N/A", df["time:timestamp"].values)
        self.assertTrue((df["time:timestamp"].apply(lambda x: isinstance(x, pd.Timestamp))).all())
        self.assertTrue((df["time:end_timestamp"].apply(lambda x: isinstance(x, pd.Timestamp))).all())
