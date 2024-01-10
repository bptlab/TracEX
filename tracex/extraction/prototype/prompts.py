# pylint: disable=import-error
"""Module providing the needed prompts for the gpt_queries."""
import random

from openai import OpenAI
from . import utils as u

client = OpenAI(api_key=u.oaik)


def create_patient_journey_context():
    """Creation of a patient journey."""
    print("Generation in progress: [----------] 0%", end="\r")
    sex = get_sex()
    print("Generation in progress: [▬---------] 10%", end="\r")
    country = get_country()
    print("Generation in progress: [▬▬--------] 20%", end="\r")
    date = get_date()
    print("Generation in progress: [▬▬▬-------] 30%", end="\r")
    life_circumstances = get_life_circumstances(sex)
    print("Generation in progress: [▬▬▬▬▬-----] 50%", end="\r")
    return (
        "Imagine being a "
        + sex
        + " person from "
        + country
        + ", that was infected with Covid19. You had first symptoms on "
        + date
        + "."
        + life_circumstances
    )


def get_sex():
    """Randomizing sex."""
    if random.randrange(2) == 0:
        return "male"
    return "female"


def get_country():
    """Randomizing country."""
    message = [{"role": "user", "content": "Please give me one european country."}]
    country = client.chat.completions.create(
        model=u.MODEL, messages=message, max_tokens=50, temperature=0.2
    )
    return country.choices[0].message.content


def get_date():
    """Randomizing date."""
    message = [
        {
            "role": "user",
            "content": "Please give me one date between 01/01/2020 and 01/09/2023.",
        }
    ]
    country = client.chat.completions.create(
        model=u.MODEL, messages=message, max_tokens=50, temperature=0.5
    )
    return country.choices[0].message.content


def get_life_circumstances(sex):
    """Randomizing life circumstances."""
    message = [{"role": "user", "content": life_circumstances_prompt(sex)}]
    life_circumstances = client.chat.completions.create(
        model=u.MODEL, messages=message, max_tokens=100, temperature=1
    )
    return life_circumstances.choices[0].message.content


def life_circumstances_prompt(sex):
    """Prompt for the life circumstances randomization."""
    return (
        "Please give me a short description of the life circumstances of an imaginary "
        + sex
        + " person in form of continous text."
        + """
        Please give me a short description of the life circumstances of an imaginary "+" person in form of continous text.
        Write the text from a second-person perspective. Something like "You are a 51-year-old Teacher" and so forth.
        Inlcude the age, the job and the family status.
        Please do not include more than 50 words.
        """
    )


CREATE_PATIENT_JOURNEY_PROMPT = """
    Please outline the course of your covid19 infection, what you did (and when you did that) because of it and which doctors you may consulted.
    Please give some information about the time, in a few cases directly as a date and in the other as something in the lines of 'in the next days', 'the week after that' or similar.
    Give your outline as a continous text.
    Also include if you later went for getting a vaccine and if so, how often. You don't have to include deails about who you are.
    Please include 100 to 400 words, but not more than 400.
"""

# Conversion of a text to bulletpoints focused on the course of a disease
TEXT_TO_EVENTINFORMATION_CONTEXT = """
    You are a summarizing expert for diseases and your job is to summarize a given text into event information regarding all important points about the course of the disease.
    Every event information has to be a short description that must not longer than 6 words.
    Every information that is not important for the course of the disease should be discarded!
    The event info has to be kept in present continous tense and should begin with a verb!
    You must not include any dates or information about the time and focus on the main aspects you want to convey.
    You should not take two actions in one event information, but rather split them into two.
    Try not to include enumerations.
"""
TEXT_TO_EVENTINFORMATION_PROMPT = """
    Here is the text from which you should extract event information:
"""
TEXT_TO_EVENTINFORMATION_ANSWER = """
    For example the text 'On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever.
    Four days later I went to the doctor and got tested positive for Covid19.' should be summarized as
    'experiencing mild symptoms, visiting doctor's, testing positive for Covid19'.
    When there is information about symptoms and a timespan in which these symptoms occured, you should summarize that as 'starting to experience symptoms, ending to experience symptoms'.
    Similarly, when there is information about a hospitalization and a timespan of it, you should summarize that as 'getting admissioned to hospital, getting discharged from hospital'.
    The text 'Concerned about my condition, I contacted my primary care physician via phone. He advised me to monitor my symptoms and stay at home unless they became severe.'
    should be summarized as 'contacting primary care physician, monitoring symptoms at home'.
    Anything like 'the following days I waited for the symptoms to fade away' should be summarized as something like 'offsetting symptoms'.
    'First symptoms on 01/04/2020' should be summarized as 'starting to experience symptoms'.
    'On July 15, 2022, I started experiencing the first symptoms of Covid-19. Initially, I had a mild cough and fatigue.' should be summarized as 'starting to experience symptoms'.
"""


# Adding of a start date to every bulletpoint
START_DATE_CONTEXT = """
    You are an expert in text understanding and your job is to take a given text and a given bulletpoint and to extract a start date to this bulletpoint.
    Just output the extracted start date.
    The date should be extracted from the text or from the context and should be as precise as possible.
    Please use the format YYYYMMDD for the dates and extend every date by "T0000".
    If the text talks about getting medication and then improving and the bulletpoint says 'improving', you should return the date of getting the medication as start date.
    If there is a conclusion at the end of the text and an outlook set the start date of the last bulletpoint to the start date of the corresponding bulletpoint.
    If there is really no information about the start date to be extracted from the text but there is information about events happening at the same time,
    use that information to draw conclusions about the start dates.
    If there is only a month specified, use the first of this month as start date.
"""
START_DATE_PROMPT = """
    Here is the text and the bulletpoint for which you should extract the start date in the format YYYYMMDD with the postfix T0000! Please always use this format!
"""
START_DATE_ANSWER = """
    For example for the text 'On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever.
    Four days later I went to the doctor and got tested positive for Covid19. In June I got infected again.' and the bulletpoints
    'experiencing mild symptoms' you should return '20200401T0000'.
    If the bulletpoint is 'testing positive for Covid19' you should return '20200405T0000'.
    The bulletpoint 'getting infected again' should be returned as '20200601T0000'.
"""
FC_START_DATE_CONTEXT = """
   You are an expert in extracting information. You easily detect the start dates in the format YYYYMMDD with the postfix 'T0000' and extract them as they are without changing any format.
"""
FC_START_DATE_PROMPT = """
    Please extract the following start date of the text without changing the given date format:
"""

# Adding of a end date to every bulletpoint
END_DATE_CONTEXT = """
    You are an expert in text understanding and your job is to take a given text and a given bulletpoint with a start date and to extract a end date to this bulletpoint.
    It is important, that an end date is extracted, even if it is the same as the start date.
    The information about the end date should be extracted from the text or from the context and should be as precise as possible.
    Please use the format YYYYMMDD for the dates and extend every date by "T0000".
    If the duration of an event is given, use that information to draw conclusions about the end date.
    If the duration of an event is not given, use the context to draw conclusions about the end date.
    Think about how long humans tend to stay in hospitals, how long it takes to recover from a disease, how long they practice new habits and so on.
    If there is no information about the end date at all, please state the start date also as the end date.
    Only return the date! Nothing else!
"""
END_DATE_PROMPT = """
    Here is the text and the bulletpoint with the start date for which you should extract end date in the format YYYYMMDD with the postfix T0000!
"""
END_DATE_ANSWER = """
    For example for the text 'Four days after the first april 2020 I went to the doctor and got tested positive for Covid19. I was then hospitalized for two weeks.'
    and the bulletpoint 'visiting doctor's' with the start date '20200405T0000' you should only return '20200405T0000'.
    For the bulletpoint 'testing positive for Covid19' with the start date '20200405T0000' you should only return '20200405T0000'.
    For the bulletpoint 'getting hospitalized' with the start date '20200405T0000' you should only return '20200419T0000'.

    The text 'In the next time I made sure to improve my mental wellbeing.' and the bulletpoint 'improving mental wellbeing' with the start date '20210610T0000', you should output '20210710T0000'.
"""
FC_END_DATE_CONTEXT = """
    You are an expert in extracting information. You easily detect the end dates in the format YYYYMMDD with the postfix 'T0000' and extract them as they are without changing any format.
"""
FC_END_DATE_PROMPT = """
    Please extract the following end date of the text without changing the given date format:
"""

# Adding of a duration to every bulletpoint
DURATION_CONTEXT = """
    You are an expert in text understanding and your job is to take a given text and given summarizing bulletpoint with a start and end date and to add a duration to this bulletpoint.
    It is important, that the bulletpoint gets a duration, even if the duration is zero, as the event happens only in a moment.
    The information about the duration should be extracted from the text or from the context and should be as precise as possible.
    Please use the format HH:MM:SS for the durations.
    If the duration of an event is given, use that information directly.
    If the duration of an event is not given, use the context to draw conclusions about it.
    If the duration is given in days, weeks or months, convert it to hours.
    Think about how long humans tend to stay in hospitals, how long it takes to recover from a disease, how long they practice new habits and so on.
    If there is no information about duration at all, please state that by computing the duration as the timedelta between the start and the end date (or 00:00:00).
    The only output should be the duration, nothing else!
"""
DURATION_PROMPT = """
    Here is the text and the bulletpoints with their start dates for which you should extract the durations in the format HHH:MM:SS. Be sure to use this format and to convert days or weeks in hours!
"""
DURATION_ANSWER = """
    For example for the text
    'Four days after the first april 2020 I went to the doctor and got tested positive for Covid19. I was then hospitalized for two weeks.'
    and the bulletpoint 'visiting doctor's' with the start date '20200405T0000' and the end date '20200405T0000' you should return '02:00:00' as this is a reasonable duration for a doctor's visit.
    For the bulletpoint 'testing positive for Covid19' with the start date '20200405T0000' and the end date '20200405T0000' you should return '00:30:00' as this is a reasonable duration for a Covid19 testing.
    For 'getting hospitalized', start date: '20200405T0000', end date: '20200419T0000' you return '336:00:00' as this is the convertion of 14 days into hours.
    The text 'In the next time I made sure to improve my mental wellbeing.' and the bulletpoint 'improving mental wellbeing' with start on '20210610T0000' and end on '20210624T0000' should return '336:00:00'.
"""
FC_DURATION_CONTEXT = """
    You are an expert in extracting information. You easily detect durations in the format HHH:MM:SS and extract them as they are without changing any format.
"""
FC_DURATION_PROMPT = """
    Please extract the following duration of the text without changing the given date format:
"""


# Adding of a event type to every bulletpoint
EVENT_TYPE_CONTEXT = """
    You are an expert in text categorization and your job is to take a given bulletpoint and to add one of given event type to it.
    The given event types are 'Symptom Onset', 'Symptom Offset', 'Diagnosis', 'Doctor visit', 'Treatment', 'Hospital stay', 'Medication', 'Lifestyle Change' and 'Feelings'.
    It is important, that every bulletpoint gets an event type.
    Furthermore it is really important, that that event type is correct and not 'Other'.
    The only output should be the event type!
"""
EVENT_TYPE_PROMPT = """
    Here is the bulletpoint for which you should extract the event type:
"""
EVENT_TYPE_ANSWER = """
    For example for the bulletpoint 'visiting doctor's' you should return 'Doctors Visit'.
    For 'testing positive for Covid19' you should return 'Diagnosis' and for 'getting hospitalized' you should return 'Hospital stay'.
"""
FC_EVENT_TYPE_CONTEXT = """
    You are an expert in extracting information. You easily detect event types and extract them as they are without changing any format. The only possible event types are
    'Symptom Onset', 'Symptom Offset', 'Diagnosis', 'Doctor visit', 'Treatment', 'Hospital stay', 'Medication', 'Lifestyle Change' and 'Feelings'.
"""
FC_EVENT_TYPE_PROMPT = """
    Please extract the following event type of the text without changing the given format:
"""

# Adding of a location type to every bulletpoint
LOCATION_CONTEXT = """
    You are an expert in text categorization and your job is to take a given bulletpoint and a category and to add one of given locations to it.
    The given locations are 'Home', 'Hospital' and 'Doctors'.
    Take the category but also the content of the bulletpoint into account.
    If it is unclear, where the person is, please use 'Home'.
    It is important, that every bulletpoint gets a location.
    Furthermore it is really important, that that location is correct.
    The only output should be the location.
"""
LOCATION_PROMPT = """
    Here is the bulletpoint for which you should extract the location:
"""
LOCATION_ANSWER = """
    For example for the bulletpoints 'visiting doctor's', you should return 'Doctors'.
    For the point 'testing positive for Covid19', you also should return 'Doctors'.
    For 'getting hospitalized' the output is 'Hospital'.
"""
FC_LOCATION_CONTEXT = """
    You are an expert in extracting information. You easily detect locations and extract them as they are without changing any format.
    The only possible locations are 'Home', 'Hospital', 'Doctors' and 'Other'.
"""
FC_LOCATION_PROMPT = """
    Please extract the following location of the text without changing the given date format:
"""
