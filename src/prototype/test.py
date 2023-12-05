import utils as u
import prompts as p
import json
import openai
from pathlib import Path
import input_handling as ih

MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1100
TEMPERATURE_SUMMARIZING = 0
FUNCTIONS= [

        {
            "name": "add_start_dates",
            "description": "Append to every bulletpoint a start date based on the input text.",
            "parameters":{
                "type": "object",
                "properties": {
                    "output": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "the updated bulletpoint with start date"
                        },
                        "description": "List updated bullet points with start date"
                    }
                   },
                "required": ["output"]
            }
        }

        
]



BULLETPOINTS_START_DATE_CONTEXT = """
    You are an expert in text understanding and your job is to take a given text and given summarizing bulletpoints and to add a start date to every bulletpoint.
    The information about the start date should be extracted from the text or from the context and should be as precise as possible.
    For example for the text 'On April 1, 2020, I started experiencing mild symptoms' it should look like this 'experiencing mild symptoms, 20200401T0000'.
    If the text talks about getting medication and then improving and the bullet point says 'improving', you should return the date of getting the medication as start date.
    """
BULLETPOINTS_START_DATE_PROMPT = """
    Here is the text and the bulletpoints for which you should extract start dates:
"""
BULLETPOINTS_START_DATE_ANSWER = """
"""





inp = open("content/inputs/journey_synth_covid_1.txt", "r").read()
bulletpoints = open("content/outputs/intermediates/1_bulletpoints.txt", "r").read()
# messages = [
#         {"role": "system", "content": BULLETPOINTS_START_DATE_CONTEXT},
#         {
#             "role": "user",
#             "content": BULLETPOINTS_START_DATE_PROMPT + inp + "\n" + bulletpoints,
#         },
#         {"role": "assistant", "content": BULLETPOINTS_START_DATE_ANSWER},
#     ]
messages = [
        {"role": "system", "content": p.TXT_TO_BULLETPOINTS_CONTEXT},
        {"role": "user", "content": p.TXT_TO_BULLETPOINTS_PROMPT + inp},
        {"role": "assistant", "content": p.TXT_TO_BULLETPOINTS_ANSWER},
    ]

    


function_call_reply = u.query_gpt(messages, function_call={'name':"convert_text_to_bulletpoints"})
print(function_call_reply)

# response = openai.ChatCompletion.create(
#         model=MODEL,
#         messages=messages,
#         max_tokens=MAX_TOKENS,
#         temperature=0,
#         functions=FUNCTIONS,
#         function_call={'name':"add_start_dates"},
#     )

# print(response)

# current_function = ih.add_start_dates(inp, bulletpoints)
# print(current_function)

# reply = json.loads(reply['choices'][0]['message']['function_call']['arguments'])
# bulletpoints = reply['bulletpoints']
# print(bulletpoints)

