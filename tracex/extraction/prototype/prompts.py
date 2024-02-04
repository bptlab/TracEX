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
TEXT_TO_EVENT_INFORMATION_CONTEXT = """
    You are a summarizing expert for diseases and your job is to summarize a given text into event information regarding all important points about the course of the disease.
    Every event information has to be a short description that must not longer than 6 words.
    Every information that is not important for the course of the disease should be discarded!
    The event info has to be kept in present continous tense and should begin with a verb!
    You must not include any dates or information about the time and focus on the main aspects you want to convey.
    You should not take two actions in one event information, but rather split them into two.
    Try not to include enumerations.
"""
TEXT_TO_EVENT_INFORMATION_PROMPT = """
    Here is the text from which you should extract event information:
"""
TEXT_TO_EVENT_INFORMATION_ANSWER = """
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
    If there is only a month specified, use the first of this month as start date. If there is no date specified in the text conclude 'N/A'.
"""
START_DATE_PROMPT = """
    Here is the text and the bulletpoint for which you should extract the start date in the format YYYYMMDD with the postfix T0000!
    In case that you are not able to find a start date return the term "N/A". Only use the format YYYYMMDDTHHMM e.g. 20200401T0000!
    Explain step by step your conclusions if the date YYYYMMDDTHHMM is available or N/A.
"""
START_DATE_ANSWER = """
    For example for the text 'On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever.
    Four days later I went to the doctor and got tested positive for Covid19. In June I got infected again. After that I had a back pain.' and the bulletpoints
    'experiencing mild symptoms' you should return '20200401T0000'.
    If the bulletpoint is 'testing positive for Covid19' you should return '20200405T0000'.
    The bulletpoint 'getting infected again' has only specified the month therefore the day is always the first of month and should be returned as '20200601T0000'.
    Futhermore the bulletpoint 'having back pain' hasn't specified a date in the text and context, therefore the date ist 'N/A'.
"""
FC_START_DATE_CONTEXT = """
   You are an expert in extracting information. You easily detect the start dates in the format YYYYMMDD with the postfix 'T0000' and extract them as they are without changing any format.
"""
FC_START_DATE_PROMPT = """
    What is the start date of given bulletpoint in the format YYYYMMDDT000 (e.g. 20200101T000). If no start date is available extract N/A.
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
    Here is the text and the bulletpoint with the start date for which you should extract the end date in the format YYYYMMDD with the postfix T0000!
    In case that you are not able to find a end date return the term "N/A". Only use the format YYYYMMDDTHHMM e.g. 20200401T0000!
    Explain step by step your conclusions if the end date YYYYMMDDTHHMM is available, if not calculate the average time of the activity and add this on the start date resulting as the end date.
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
    You are an expert in text categorization and your job is to take given event information and to add one of given event type to every event information.
    The given event types are 'Symptom Onset', 'Symptom Offset', 'Diagnosis', 'Doctor visit', 'Treatment', 'Hospital admission', 'Hospital discharge', 'Medication', 'Lifestyle Change' and 'Feelings'.
    It is important, that every event information gets an event type.
    Furthermore it is really important, that that event type is correct and not 'Other'.
    The only output should be the event type!
"""
EVENT_TYPE_PROMPT = """
    You will be given a bulletpoint of a patient journey.
    Classify the bulletpoint into one of the following event types: Symptom Onset, Symptom Offset, Diagnosis, Doctor visit, Treatment, Hospital stay, Medication, Lifestyle Change and Feelings.
    Return only the name of the event type, and nothing else.
    MAKE SURE your output is one of the nine event types stated. ONLY return the name of the event type, and nothing else!

"""
EVENT_TYPE_ANSWER = """
    For example for the event information 'visiting doctor's' you should output 'Doctors Visit'.
    For 'testing positive for Covid19' you should output 'Diagnosis' and for 'getting hospitalized' you should output 'Hospital stay'.
"""

# Adding of a location type to every bulletpoint
LOCATION_CONTEXT = """
    You are an expert in text categorization and your job is to take given bulletpoints and to add one of given locations to every bulletpoint.
    The given locations are 'Home', 'Hospital' and 'Doctors'.
    If it is unclear, where the person is, please use 'Home'.
    It is important, that every bullet point gets an event type.
    Furthermore it is really important, that that event type is correct.
    The only (!) output should be the updated bullet points, nothing else!
    Please do not add a phrase like "here are your bulletpoints" or something like that..
"""
LOCATION_PROMPT = """
    You will be given a bulletpoint and the according event type of a patient journey.
    Classify the bulletpoint into one of the following locations: Home, Hospital and Doctors.
    Return only the name of the location, and nothing else. Make sure only to return the name of the location, and nothing else!
"""
LOCATION_ANSWER = """
    For example for the bulletpoints 'visiting doctor's', you should return 'Doctors'.
    For the point 'testing positive for Covid19', you also should return 'Doctors'.
    For 'getting hospitalized' the output is 'Hospital'.
"""

############################################## METRICS ##############################################


METRIC_EVENT_INFORMATION_CONTEXT = """
    You are an expert in text categorization and your job is to take given bulletpoint and to add one of the given relevance categories to every bulletpoint.
    The categories are as follows: Not Relevant, Low Relevance, Moderate Relevance, High Relevance and Critical Relevance.
    It is important, that every bulletpoint gets a relevance category.
    Furthermore it is really important, that that relevance category is correct.
    The only output should be the relevance category!
    Please do not add a phrase like "here are your bulletpoints" or something like that..

    The relevance categories are defined as follows:
    Not Relevant: The event has minimal or no impact on understanding the course of the disease.
    Low Relevance: The event has limited importance in grasping the disease's progression.
    Moderate Relevance: The event provides some insight into the course of the disease but is not crucial.
    High Relevance: The event significantly contributes to understanding the disease's progression.
    Critical Relevance: The event is crucial for comprehending the disease's course and has a major impact on its understanding and management.

"""
METRIC_EVENT_INFORMATION_PROMPT = """
    Please classify to given bulletpoint one of the following categories: Not Relevant, Low Relevance, Moderate Relevance, High Relevance and Critical Relevance.
    Only output the name of the category, and nothing else. You MUST NOT include any other information.
    For example, if the bulletpoint is 'visiting doctor's', you should output 'High Relevance'.
"""

METRIC_TIMESTAMPS_CONTEXT = """
    You are an expert in text understanding and your job is to take a given text and to check if the given start date and end date of an given bulletpoint are correct based on the given patient journey.
    Correct is a start and end date in the format YYYYMMDDTHHMM if the date is appearing in the patient journey related to bulletpoint.
    If the start date and end date appearing in the context of the bulletpoint, you should output True.
    If there is another start or end date in the patient journey, the given timestamps are wrong and you should output False.
    If the start or end date is not appearing in the patient journey, it could be that the timestamp is estimated. In this case check if
    the estimation is reasonable and output True if it is and False if it is not.
    The only output should be the True or False, and nothing else.
"""


METRIC_TIMESTAMPS_PROMPT = """
    Please check if the given start date and end date of an given bulletpoint are correct based on the given patient journey.

    Is the following start and end date correct in the context of the bulletpoint based on the given patient journey?
    Only output the True or False, and nothing else. You MUST NOT include any other information.
"""
