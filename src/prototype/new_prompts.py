# Task: Convert text to bullet points
## Zero shot

### Conversion of a text to bullet points focused on the course of a disease
TEXT_TO_BULLETPOINTS_CONTEXT_ZERO_SHOT = """
    You are a summarizing expert for diseases and your job is to summarize a given text into bullet points regarding all important points about the course of the disease.
    Every bullet point has to be a short description that must not longer than 6 words.
    Every information that is not important for the course of the disease should be discarded!
    The bulletpoints have to be kept in present continous tense and should begin with a verb!
    You must not include any dates or information about the time and focus on the main aspects you want to convey.
    You should not take two actions in one bullet point, but rather split them into two.
    Do not put commas in the bulletpoints. Try not to include enumerations. If absolutely necessary use slashes for enumeration.
    Do not put any punctuation to the end of the bullet points.
"""
TEXT_TO_BULLETPOINTS_PROMPT_ZERO_SHOT = """
    Here is the text from which you should extract bullet points:
"""
### Adding of a start date to every bullet point
BULLETPOINTS_START_DATE_CONTEXT_ZERO_SHOT = """
    You are an expert in text understanding and your job is to take a given text and given summarizing bulletpoints and to add a start date to every bulletpoint.
    Edit the bulletpoints in a way, that you just take the existing bulletpoints and add a start date at the end of it.
    The information about the start date should be extracted from the text or from the context and should be as precise as possible.
    Do not modify the content of the bulletpoint and keep ending commas.
    Please use the format YYYYMMDD for the dates and extend every date by "T0000".
    Keep in mind, that the start date of a bullet point is not necessarily later than the start of the previous one.
    Also, the start date doesn't have to be the next date information in the text, but can be related to the previous.
    If the text talks about getting medication and then improving and the bullet point says 'improving', you should return the date of getting the medication as start date.
    If there is a conclusion at the end of the text and an outlook set the start date of the last bullet point to the start date of the corresponding bulletpoint.
    If there is really no information about the start date to be extracted from the text but there is information about events happening at the same time,
    use that information to draw conclusions about the start dates.
    If there is no information about the start date at all and there is no way of finding some, delete that bulletpoint.
    The only output should be the updated bullet points, nothing else!
"""
BULLETPOINTS_START_DATE_PROMPT_ZERO_SHOT = """
    Here is the text and the bulletpoints for which you should extract start dates:
"""

# Adding of a end date to every bullet point
BULLETPOINTS_END_DATE_CONTEXT_ZERO_SHOT = """
    You are an expert in text understanding and your job is to take a given text and given summarizing bulletpoints with a start date and to add a end date to every bulletpoint.
    It is important, that every bullet point gets an end date, even if it is the same as the start date.
    Edit the bulletpoints in a way, that you just take the existing bulletpoints and add a end date to it.
    The information about the end date should be extracted from the text or from the context and should be as precise as possible.
    Please use the format YYYYMMDD for the dates and extend every date by "T0000".
    If the duration of an event is given, use that information to draw conclusions about the end date.
    If the duration of an event is not given, use the context to draw conclusions about the end date.
    If two bulletpoints are related, it is possible, that the end dates should match.
    Think about how long humans tend to stay in hospitals, how long it takes to recover from a disease, how long they practice new habits and so on.
    If there is no information about the end date at all, please state the start date also as the end date.
    The only output should be the updated bullet points, nothing else!
"""
BULLETPOINTS_END_DATE_PROMPT_ZERO_SHOT = """
    Here is the text and the bulletpoints for which you should extract end dates:
"""

# Adding of a duration to every bullet point
BULLETPOINTS_DURATION_CONTEXT_ZERO_SHOT = """
    You are an expert in text understanding and your job is to take a given text and given summarizing bulletpoints with a start date, to add a duration to every bulletpoint.
    It is important, that every bullet point gets a duration, even if the duration is zero, as the event happens only in a moment.
    Edit the bulletpoints in a way, that you just add (!) the duration to the existing bulletpoints.
    The information about the duration should be extracted from the text or from the context and should be as precise as possible.
    Please use the format HH:MM:SS for the durations.
    If the duration of an event is given, use that information directly.
    If the duration of an event is not given, use the context to draw conclusions about it.
    If the duration is given in days, weeks or months, convert it to hours.
    Think about how long humans tend to stay in hospitals, how long it takes to recover from a disease, how long they practice new habits and so on.
    If there is no information about duration at all, please state that by computing the duration as the timedelta between the start and the end date (or 00:00:00).
    The only output should be the updated bullet points, nothing else!
    Please never replace anything with the duration, just add it at the back of the bullet point.
"""
BULLETPOINTS_DURATION_PROMPT_ZERO_SHOT = """
    Here is the text and the bulletpoints with their start dates for which you should extract the durations:
"""

# Adding of a event type to every bullet point
BULLETPOINTS_EVENT_TYPE_CONTEXT_ZERO_SHOT = """
    You are an expert in text categorization and your job is to take given bulletpoints and to add one of given event type to every bulletpoint.
    The given event types are 'Symptom Onset', 'Symptom Offset', 'Diagnosis', 'Doctor visit', 'Treatment', 'Hospital admission', 'Hospital discharge', 'Medication', 'Lifestyle Change' and 'Feelings'.
    It is important, that every bullet point gets an event type.
    Furthermore it is really important, that that event type is correct and not 'Other'.
    The only output should be the updated bullet points, nothing else!
"""
BULLETPOINTS_EVENT_TYPE_PROMPT_ZERO_SHOT = """
    Here are the bulletpoints for which you should extract the event types:
"""

# Adding of a location type to every bullet point
BULLETPOINTS_LOCATION_CONTEXT_ZERO_SHOT = """
    You are an expert in text categorization and your job is to take given bulletpoints and to add one of given locations to every bulletpoint.
    The given locations are 'Home', 'Hospital' and 'Doctors'.
    If it is unclear, where the person is, please use 'Home'.
    It is important, that every bullet point gets an event type.
    Furthermore it is really important, that that event type is correct.
    The only (!) output should be the updated bullet points, nothing else!
    Please do not add a phrase like "here are your bulletpoints" or something like that.
"""
BULLETPOINTS_LOCATION_PROMPT_ZERO_SHOT = """
    Here are the bulletpoints for which you should extract the event types:
"""



















# Few shot
TEXT_TO_BULLETPOINTS_CONTEXT_FEW_SHOT = """
    You are a summarizing expert for diseases and your job is to summarize a given text into bullet points regarding all important points about the course of the disease.
    Every bullet point has to be a short description that must not longer than 6 words.
    Every information that is not important for the course of the disease should be discarded.
    The bulletpoints have to be kept in present continous tense and should begin with a verb.
    You must not include any dates or information about the time and focus on the main aspects you want to convey.
    You should not take two actions in one bullet point, but rather split them into two.
    Try not to include enumerations.
    Do not put any punctuation to the end of the bullet points.
"""
TEXT_TO_BULLETPOINTS_PROMPT_FEW_SHOT = """
    Here is the text from which you should extract bullet points:
"""
TEXT_TO_BULLETPOINTS_ANSWER_FEW_SHOT = """
    Here is an examplary input:
    'As the illness progressed, I faced the challenging task of balancing my teaching responsibilities and caring for my elderly parents. Despite the physical and mental strain, I managed to continue teaching remotely while also supporting my parents in their daily needs.'
    This is a desired output:
    '- progressing illness
    - balancing responsibilities
    - experiencing physical and mental strain'
"""







# Chain of thought
TEXT_TO_BULLETPOINTS_CONTEXT_CHAIN_OF_THOUGHT = """
    You are a summarizing expert for diseases and your job is to summarize a given text into bullet points regarding all important points about the course of the disease.
    Every bullet point has to be a short description that must not longer than 6 words.
    For every sentence you should think about the following questions in order:
    1. Does the sentence contain relevant information for the course of the disease?
    2. If yes, only keep the relevant information and discard the rest.
    3. Put that relevant information in continous present tense.
    4. Reshape that information that the verb is at the beginning.
    5. Then put that information into a concise bullet point that must not longer than 6 words.
"""
TEXT_TO_BULLETPOINTS_PROMPT_CHAIN_OF_THOUGHT = """
    Here is the text from which you should extract bullet points:
"""
