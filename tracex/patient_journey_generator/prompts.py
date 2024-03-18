"""File containing all prompts for the patient journey generation."""

CREATE_PATIENT_JOURNEY_PROMPT = """
    Please outline the course of your Covid-19 infection, what you did (and when you did that) because of it and which
    doctors you may consulted.
    Please give some information about the time, in a few cases directly as a date and in the other as something in the
    lines of 'in the next days', 'the week after that' or similar.
    Give your outline as a continuous text. Also include if you later went for getting a vaccine and if so, how often.
    You don't have to include deals about who you are. Please include 100 to 400 words, but not more than 400.
"""