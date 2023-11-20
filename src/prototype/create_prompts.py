import os

import openai

import constants as c

openai.api_key = c.oaik

NEW_PROMPTS_CONTEXT = """
    You are an expert prompt engineer for gpt-3.5-turbo. You are tasked with creating the best possible prompts for given tasks.
    Your prompts should consist of three parts, one for the system, one for user and one for assistant.
    """
NEW_PROMPTS_PROMPT = """
    The task, for which you have to create a prompt is: Given a text and summarizing bullet points,
    how can you tell a gpt model to extract a duration in the format HH:MM:SS for every event captured as a bullet point?
    """
NEW_PROMPTS_ANSWER = """"""

messages = [
    {"role": "system", "content": NEW_PROMPTS_CONTEXT},
    {"role": "user", "content": NEW_PROMPTS_PROMPT},
    {"role": "assistant", "content": NEW_PROMPTS_ANSWER},
]
new_prompts = openai.ChatCompletion.create(
    model=c.MODEL,
    messages=messages,
    max_tokens=c.MAX_TOKENS,
    temperature=c.TEMPERATURE_CREATION,
)
output = new_prompts.choices[0].message.content
with open(
    os.path.join(c.out_path, "new_prompts.txt"),
    "w",
) as f:
    f.write(output)
