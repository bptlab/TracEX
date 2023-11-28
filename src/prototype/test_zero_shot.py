import utils as u
import new_prompts as p



def convert_text_to_bulletpoints(inp):
    """Converts the input text to bulletpoints."""
    messages = [
        {"role": "system", "content": p.TEXT_TO_BULLETPOINTS_CONTEXT_ZERO_SHOT},
        {"role": "user", "content": p.TEXT_TO_BULLETPOINTS_PROMPT_ZERO_SHOT + inp},
    ]
    bulletpoints = u.query_gpt(messages)
    bulletpoints = remove_commas(bulletpoints)
    bulletpoints = add_ending_commas(bulletpoints)
    with open((u.out_path / "intermediates/1_bulletpoints_zero_shot.txt"), "w") as f:
        f.write(bulletpoints)
    print (bulletpoints + '\n'+ '\n')
    return bulletpoints



def add_start_dates(inp, bulletpoints):
    """Adds start dates to the bulletpoints."""
    messages = [
        {"role": "system", "content": p.BULLETPOINTS_START_DATE_CONTEXT_ZERO_SHOT},
        {
            "role": "user",
            "content": p.BULLETPOINTS_START_DATE_PROMPT_ZERO_SHOT + inp + "\n" + bulletpoints,
        }
    ]
    bulletpoints_start = u.query_gpt(messages)
    bulletpoints_start = add_ending_commas(bulletpoints_start)
    with open(
        (u.out_path / "intermediates/2_bulletpoints_with_start_zero_shot.txt"),
        "w",
    ) as f:
        f.write(bulletpoints_start)

    print (bulletpoints_start)
    return bulletpoints_start


def add_end_dates(inp, bulletpoints):
    """Adds end dates to the bulletpoints."""
    messages = [
        {"role": "system", "content": p.BULLETPOINTS_END_DATE_CONTEXT_ZERO_SHOT},
        {
            "role": "user",
            "content": p.BULLETPOINTS_END_DATE_PROMPT_ZERO_SHOT + inp + "\n" + bulletpoints,
        }
    ]
    bulletpoints_start = u.query_gpt(messages)
    bulletpoints_start = add_ending_commas(bulletpoints_start)
    with open(
        (u.out_path / "intermediates/3_bulletpoints_with_end_zero_shot.txt"),
        "w",
    ) as f:
        f.write(bulletpoints_start)
    print(bulletpoints_start)
    return bulletpoints_start


def add_durations(inp, bulletpoints_start):
    """Adds durations to the bulletpoints."""
    messages = [
        {"role": "system", "content": p.BULLETPOINTS_DURATION_CONTEXT_ZERO_SHOT},
        {
            "role": "user",
            "content": p.BULLETPOINTS_DURATION_PROMPT_ZERO_SHOT + inp + "\n" + bulletpoints_start,
        }
    ]
    bulletpoints_duration = u.query_gpt(messages)
    bulletpoints_duration = add_ending_commas(bulletpoints_duration)
    with open(
        (u.out_path / "intermediates/4_bulletpoints_with_duration_zero_shot.txt"),
        "w",
    ) as f:
        f.write(bulletpoints_duration)
    print(bulletpoints_duration)
    return bulletpoints_duration


def add_event_types(bulletpoints_durations):
    """Adds event types to the bulletpoints."""
    messages = [
        {"role": "system", "content": p.BULLETPOINTS_EVENT_TYPE_CONTEXT_ZERO_SHOT},
        {
            "role": "user",
            "content": p.BULLETPOINTS_EVENT_TYPE_PROMPT_ZERO_SHOT + bulletpoints_durations,
        }
    ]
    bulletpoints_event_type = u.query_gpt(messages)
    bulletpoints_event_type = add_ending_commas(bulletpoints_event_type)
    with open(
        (u.out_path / "intermediates/5_bulletpoints_with_event_type_zero_shot.txt"),
        "w",
    ) as f:
        f.write(bulletpoints_event_type)
    print(bulletpoints_event_type)
    return bulletpoints_event_type


def add_locations(bulletpoints_event_types):
    """Adds locations to the bulletpoints."""
    messages = [
        {"role": "system", "content": p.BULLETPOINTS_LOCATION_CONTEXT_ZERO_SHOT},
        {
            "role": "user",
            "content": p.BULLETPOINTS_LOCATION_PROMPT_ZERO_SHOT + bulletpoints_event_types,
        }
    ]
    bulletpoints_location = u.query_gpt(messages)
    bulletpoints_location = remove_brackets(bulletpoints_location)
    with open(
        (u.out_path / "intermediates/6_bulletpoints_with_location_zero_shot.txt"),
        "w",
    ) as f:
        f.write(bulletpoints_location)
    print(bulletpoints_location)
    return bulletpoints_location





# Datacleaning
def remove_commas(bulletpoints):
    """Removes commas from within the bulletpoints."""
    bulletpoints = bulletpoints.replace(", ", "/")
    bulletpoints = bulletpoints.replace(",", "/")
    return bulletpoints


def add_ending_commas(bulletpoints):
    """Adds commas at the end of each line."""
    bulletpoints = bulletpoints.replace("\n", ",\n")
    bulletpoints = bulletpoints + ","
    return bulletpoints


def remove_brackets(bulletpoints):
    """Removes brackets from within the bulletpoints."""
    bulletpoints = bulletpoints.replace("(", "")
    bulletpoints = bulletpoints.replace(")", "")
    bulletpoints = bulletpoints.replace("]", "")
    bulletpoints = bulletpoints.replace("[", "")
    bulletpoints = bulletpoints.replace("{", "")
    bulletpoints = bulletpoints.replace("}", "")
    return bulletpoints