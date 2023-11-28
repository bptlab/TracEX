import utils as u
import new_prompts as n
import test_zero_shot as z

input_text = open("content/inputs/journey_synth_covid_0.txt", "r").read()
bulletpoints = z.convert_text_to_bulletpoints(input_text)
# u.pause_between_queries()
bulletpoints_start = z.add_start_dates(input_text, bulletpoints)
# u.pause_between_queries()
bulletpoints_end = z.add_end_dates(input_text, bulletpoints)
# u.pause_between_queries()
bulletpoints_duration = z.add_durations(input_text, bulletpoints_end)
# u.pause_between_queries()
bulletpoints_event_type = z.add_event_types(bulletpoints_duration)
# u.pause_between_queries()
bulletpoints_location = z.add_locations(bulletpoints_event_type)



# messages = [
#     {"role": "system", "content": n.TEXT_TO_BULLETPOINTS_CONTEXT_CHAIN_OF_THOUGHT},
#     {
#         "role": "user",
#         "content": n.TEXT_TO_BULLETPOINTS_PROMPT_CHAIN_OF_THOUGHT + input_text,
#     }
#     # {"role": "assistant", "content":}
# ]
# output = u.query_gpt(messages)
# print(output)




# input_text = open("content/inputs/journey_synth_covid_0.txt", "r").read()
# messages = [
#     {"role": "system", "content": o.TXT_TO_BULLETPOINTS_CONTEXT},
#     {
#         "role": "user",
#         "content": o.TXT_TO_BULLETPOINTS_PROMPT + input_text,
#     }
#     # {"role": "assistant", "content":}
# ]
# output = u.query_gpt(messages)
# print(output)


