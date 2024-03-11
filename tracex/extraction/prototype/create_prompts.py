"""Module providing functions to produce prompts by using GPT generations."""
from openai import OpenAI
import utils as u

client = OpenAI(api_key=u.oaik)


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
NEW_PROMPTS = client.chat.completions.create(
    model=u.MODEL,
    messages=messages,
    max_tokens=u.MAX_TOKENS,
    temperature=u.TEMPERATURE_CREATION,
)
output = NEW_PROMPTS.choices[0].message.content
with open(
    (u.output_path / "new_prompts.txt"),
    "w",
) as f:
    f.write(output)
