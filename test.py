import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tracex.tracex.settings")
# pylint: enable=wrong-import-position

from tracex.extraction.prototype import input_inquiry as ii
from tracex.extraction.prototype import input_handling as ih
from tracex.extraction.prototype import output_handling as oh
from tracex.extraction.prototype import utils as u
from tracex.extraction.prototype import function_calls as fc
from tracex.extraction.prototype import prompts as p

text = open(u.input_path / "journey_synth_covid_1.txt").read()
df = ih.convert_text_to_bulletpoints(text)
print(df)
df = ih.add_start_dates(text, df)
df = ih.add_end_dates(text, df)

print(df)

df.to_csv(u.output_path / "intermediates/dataframe.csv")

# output = 'The end date for the bulletpoint "Experiencing mild cough and fatigue" and the start date 20220108T0000 is 20230911T0000.'

# fc_message = [
#     {"role": "system", "content": p.END_DATE_CONTEXT},
#     {
#         "role": "user",
#         "content": p.END_DATE_FUNCTION_CALL
#         + "The text: "
#         + output
#     },
# ]


# print(u.query_gpt(fc_message, tool_choice={ "type": "function", "function": {"name": "add_end_dates"}}))
