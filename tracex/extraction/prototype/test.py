import utils as u
import prompts as p
import prompts_old as po
import functions_calls as fc
import json
import openai
import input_handling as ih

MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1100
TEMPERATURE_SUMMARIZING = 0
FUNCTIONS = [

    {
        "name": "add_start_dates",
        "description": "Append to every bulletpoint a start date based on the input text.",
        "parameters": {
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

TOOLS = [
    # {
    #     "type": "function",
    #     "function": {
    #             "name": "convert_text_to_bulletpoints",
    #             "description": "Converts relevants parts related to the course of the disease of the input text to bulletpoints.",
    #             "parameters": {
    #                 "type": "object",
    #                 "properties": {
    #                     "output": {
    #                         "type": "array",
    #                         "items": {
    #                             "type": "string",
    #                             "description": "An extracted bullet point"
    #                         }
    #                     },
    #                 },
    #                 "required": ["output"]
    #             },
    #     }
    # },
    {
        "type": "function",
        "function": {
                "name": "append_start_dates",
                "description": "Append to every bulletpoint a start date based on the input text like this: 'experiencing mild symptoms, 20200401T0000'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "output": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "a bulletpoint with start date"
                            }
                        },
                    },
                    "required": ["output"]
                },
        }
    },
    

]


BULLETPOINTS_START_DATE_CONTEXT = """
    You are an expert in text understanding and your job is to take a given text and given bulletpoints and to append a start date to every bulletpoint.
    The information about the start date should be extracted from the text or from the context and should be as precise as possible.
    For example for the text 'On April 1, 2020, I started experiencing mild symptoms' it should look like this 'experiencing mild symptoms, 20200401T0000'.
    """
BULLETPOINTS_START_DATE_PROMPT = """
    Please add a start date to every bulletpoint and use the following format: 'experiencing mild symptoms, 20200401T0000'.
    Here is the text and the bulletpoints for which you should extract start dates:
"""
BULLETPOINTS_START_DATE_ANSWER = """
"""


inp = open("content/inputs/journey_synth_covid_1.txt", "r").read()
bulletpoints = open(
    "content/outputs/intermediates/1_bulletpoints.txt", "r").read()
messages = [
    {"role": "system", "content": BULLETPOINTS_START_DATE_CONTEXT},
    {
        "role": "user",
        "content": BULLETPOINTS_START_DATE_PROMPT + inp + "\n" + bulletpoints,
    },
    {"role": "assistant", "content": BULLETPOINTS_START_DATE_ANSWER},
]
# messages = [
#         {"role": "system", "content": p.TXT_TO_BULLETPOINTS_CONTEXT},
#         {"role": "user", "content": p.TXT_TO_BULLETPOINTS_PROMPT + inp},
#         {"role": "assistant", "content": p.TXT_TO_BULLETPOINTS_ANSWER},
#     ]


######################################### Testing with Framework #########################################

# function_call_reply = u.query_gpt(messages, function_call={'name':"convert_text_to_bulletpoints"})
# print(function_call_reply)


# current_function = ih.add_start_dates(inp, bulletpoints)
# print(current_function)

# current_function = ih.convert_text_to_bulletpoints(inp)
# print(current_function)

# reply = json.loads(reply['choices'][0]['message']['function_call']['arguments'])
# bulletpoints = reply['bulletpoints']
# print(bulletpoints)

######################################### Function Calling #########################################

# response = openai.ChatCompletion.create(
#     model=MODEL,
#     messages=messages,
#     max_tokens=MAX_TOKENS,
#     temperature=0,
#     functions=fc.FUNCTIONS,
#     function_call="auto",
# )

# print(response)

######################################### Tools Calling #########################################

response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=0,
        tools=TOOLS,
#       tool_choice={"type": "function", "function": {"name": "add_start_dates"}},
        tool_choice="auto",
    )

print(response)
