import utils as u
import new_prompts as p


input_text = open("content/inputs/journey_synth_covid_0.txt", "r").read()
messages = [
    {"role": "system", "content": p.TEXT_TO_BULLETPOINTS_CONTEXT_CHAIN_OF_THOUGHT},
    {
        "role": "user",
        "content": p.TEXT_TO_BULLETPOINTS_PROMPT_CHAIN_OF_THOUGHT + input_text,
    }
    # {"role": "assistant", "content":}
]
output = u.query_gpt(messages)
print(output)
