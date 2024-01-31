# pylint: skip-file
# pylint: enable=wrong-import-position
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tracex.tracex.settings")

from tracex.extraction.prototype import input_inquiry as ii
from tracex.extraction.prototype import input_handling as ih
from tracex.extraction.prototype import utils as u
from tracex.extraction.prototype import function_calls as fc
from tracex.extraction.prototype import metrics as m
from tracex.extraction.prototype import create_xes as x

text = open(u.input_path / "journey_synth_covid_0.txt").read()
# df = ih.convert_text_to_bulletpoints(text)
# print(df)

print(m.measure_event_information(text))


# df = m.measure_event_types(text)
# print(df)
# df = m.measure_location(text)
# print(df)
# ih.convert_dataframe_to_csv(df)
# df = ih.add_start_dates(text, df)
# print(df)
# df = ih.add_end_dates(text, df)
# print(df)
# df = ih.add_durations(df)
# print(df)
# df = ih.add_event_types(df)
# print(df)
# df = ih.add_locations(df)
# print(df)
# ih.convert_dataframe_to_csv(df)
# x.create_xes(u.output_path / "single_trace.csv", "test", "event_information")
