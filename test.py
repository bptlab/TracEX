import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tracex.tracex.settings")
# pylint: enable=wrong-import-position

from tracex.extraction.prototype import input_inquiry as ii
from tracex.extraction.prototype import input_handling as ih
from tracex.extraction.prototype import output_handling as oh
from tracex.extraction.prototype import utils as u

text = open(u.input_path / "journey_synth_covid_1.txt").read()
df = ih.convert_text_to_bulletpoints(text)
print(df)
df = ih.add_start_dates(text, df)
df = ih.add_end_dates(text, df)

print(df)
