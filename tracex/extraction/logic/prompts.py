"""File containing all prompts for the extraction logic."""

CREATE_PATIENT_JOURNEY_PROMPT = """
    Please outline the course of your Covid-19 infection, what you did (and when you did that) because of it and which
    doctors you may consulted.
    Please give some information about the time, in a few cases directly as a date and in the other as something in the
    lines of 'in the next days', 'the week after that' or similar.
    Give your outline as a continuous text. Also include if you later went for getting a vaccine and if so, how often.
    You don't have to include deals about who you are. Please include 100 to 400 words, but not more than 400.
"""


TXT_TO_EVENT_INFORMATION_CONTEXT = """
    You are a summarizing expert for diseases and your job is to summarize a given text into activity labels regarding
    all important points about the course of the disease. Every activity label has to be a short description that must
    be not longer than 4 words. Every information that is not important for the course of the disease should be
    discarded! The activity labels have to be kept in present continuous tense and should begin with a verb!
    You must not include any dates or information about the time and focus on the main aspects you want to convey.
    You should not take two actions in one activity label, but rather split them into two. Do not put commas in the
    activity labels. Try not to include enumerations. If absolutely necessary use slashes for enumeration. Do not put
    any punctuation to the end of the activity label.
"""

TXT_TO_EVENT_INFORMATION_PROMPT = """
    Here is the text from which you should extract the activity labels:
"""

TXT_TO_EVENT_INFORMATION_ANSWER = """
    For example the text 'On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue,
    and a low-grade fever. Four days later I went to the doctor and got tested positive for Covid19.' should be
    summarized to the following activity labels:
    'experiencing mild 'symptoms \n 'visiting doctor's' \n 'testing positive for Covid19'.
    When there is information about symptoms and a timespan in which these symptoms occurred, you should summarize
    that as 'starting to experience symptoms' and 'ending to experience symptoms'. Similarly, when there is information about
    a hospitalization and a timespan of it, you should summarize that as
    'Being admitted to hospital' and 'getting discharged from hospital'.
    The text 'Concerned about my condition, I contacted my primary care physician via phone. He advised me to monitor my
    symptoms and stay at home unless they became severe.' should be summarized as
    'contacting primary care physician', \n 'monitoring symptoms at home'.
    Anything like 'the following days I waited for the symptoms to fade away' should be summarized as something like
    'offsetting symptoms'. 'First symptoms on 01/04/2020' should be summarized as 'starting to experience symptoms'.
    'On July 15, 2022, I started experiencing the first symptoms of Covid-19. Initially, I had a mild cough and fatigue'
     should be summarized as 'starting to experience symptoms'.
"""


START_DATE_CONTEXT = """
    You are an expert in text understanding and your job is to take a given text and a given activity label and to
    extract a start date to this activity label. Only output the extracted start date!
    The date should be extracted from the text or from the context and should be as precise as possible.
    Please use the format YYYYMMDD for the dates and extend every date by "T0000".
    If the text talks about getting medication and then improving and the activity label says 'improving', you should
    return the date of getting the medication as start date.
    If there is a conclusion at the end of the text and an outlook set the start date of the last activity label to the
    start date of the corresponding activity label.
    If there is really no information about the start date to be extracted from the text but there is information about
    events happening at the same time,use that information to draw conclusions about the start dates.
    If there is only a month specified, use the first day of this month as the start date. For example for June it would
    be 20200601T0000. If there is no date specified in the text conclude 'N/A'.
"""

START_DATE_PROMPT = """
    Here is the text and the activity label for which you should extract the start date in the format YYYYMMDD with the
    postfix T0000!
    In case that you are not able to find a start date return the term "N/A".
    Only use the format YYYYMMDDTHHMM e.g. 20200401T0000!
    Explain step by step your conclusions if the date YYYYMMDDTHHMM is available or N/A.
"""

START_DATE_ANSWER = """
    For example for the text
    'On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever.
    Four days later I went to the doctor and got tested positive for Covid19. In June I got infected again.
    After that I had a back pain' and the activity label 'experiencing mild symptoms' you should return '20200401T0000'.
    If the activity label is 'testing positive for Covid19' you should return '20200405T0000'.
    The activity label 'getting infected again' has only specified the month therefore the day is always the first of
    month and should be returned as '20200601T0000'.Furthermore, the activity label 'having back pain' hasn't specified
    a date in the text and context, therefore the date ist 'N/A'.
"""

FC_START_DATE_CONTEXT = """
   You are an expert in extracting information. You easily detect the start dates in the format YYYYMMDD with the
   postfix 'T0000' and extract them as they are without changing any format.
"""

FC_START_DATE_PROMPT = """
    What is the start date of given activity label in the format YYYYMMDDT000 (e.g. 20200101T000).
    If no start date is available extract N/A.
"""


END_DATE_CONTEXT = """
    You are an expert in text understanding and your job is to take a given text and a given activity label with a
    start date and to extract a end date to this activity label. It is important, that an end date is extracted,
    even if it is the same as the start date. The information about the end date should be extracted from the text or
    from the context and should be as precise as possible. Please use the format YYYYMMDD for the dates and extend
    every date by "T0000".
    If the duration of an event is given, use that information to draw conclusions about the end date.
    If the duration of an event is not given, use the context to draw conclusions about the end date.
    Think about how long humans tend to stay in hospitals, how long it takes to recover from a disease,
    how long they practice new habits and so on.
    If there is no information about the end date at all, please state the start date also as the end date.
    Only return the date! Nothing else!
"""

END_DATE_PROMPT = """
    Here is the text and the activity label with the start date for which you should extract the end date in the format
    YYYYMMDD with the postfix T0000! In case that you are not able to find a end date return the term "N/A".
    Only use the format YYYYMMDDTHHMM e.g. 20200401T0000! Explain step by step your conclusions if the end date
    YYYYMMDDTHHMM is available, if not calculate the average time of the activity and add this on the start date
    resulting as the end date.
"""

END_DATE_ANSWER = """
    For example for the text 'Four days after the first april 2020 I went to the doctor and got tested positive for
    Covid19. I was then hospitalized for two weeks.' and the activity label 'visiting doctor's' with the
    start date '20200405T0000' you should only return '20200405T0000'. For the activity label
    'testing positive for Covid19' with the start date '20200405T0000' you should only return '20200405T0000'. For the
    activity label 'getting hospitalized' with the start date '20200405T0000' you should only return '20200419T0000'.

    The text 'In the next time I made sure to improve my mental well being.' and the activity label
    'improving mental well being' with the start date '20210610T0000', you should output '20210710T0000'.
"""

FC_END_DATE_CONTEXT = """
    You are an expert in extracting information. You easily detect the end dates in the format YYYYMMDD with the
    postfix 'T0000' and extract them as they are without changing any format.
"""

FC_END_DATE_PROMPT = """
    Please extract the following end date of the text without changing the given date format:
"""


EVENT_TYPE_CONTEXT = """
    You are an expert in text categorization and your job is to take a given activity label and to classify one of
    given event types to it.
    The given event types are 'Symptom Onset', 'Symptom Offset', 'Diagnosis', 'Doctor visit', 'Treatment',
    'Hospital stay', 'Medication', 'Lifestyle Change' and 'Feelings'.
    Furthermore it is really important, that that event type is correct and not 'Other'.
    The only output should be the event type!
"""

EVENT_TYPE_PROMPT = """
    Here is the activity label that you should classify to the provided event types.
    Explain step by step your conclusions your choice of the event type: 'Symptom Onset', 'Symptom Offset', 'Diagnosis',
    'Doctor visit', 'Treatment', 'Hospital stay', 'Medication', 'Lifestyle Change' and 'Feelings'
"""

EVENT_TYPE_ANSWER = """
    For example for the activity label 'visiting doctor's' you should return 'Doctors Visit'.
    For 'testing positive for Covid19' you should return 'Diagnosis' and for 'getting hospitalized'
    you should return 'Hospital stay'.
"""

FC_EVENT_TYPE_CONTEXT = """
    You are an expert in extracting information.
    You easily detect event types and extract them as they are without changing any format.
    The only possible event types are 'Symptom Onset', 'Symptom Offset', 'Diagnosis', 'Doctor visit', 'Treatment',
    'Hospital stay', 'Medication', 'Lifestyle Change' and 'Feelings'.
"""

FC_EVENT_TYPE_PROMPT = """
    Please extract the following event type of the text without changing the given format:
"""


LOCATION_CONTEXT = """
    You are an expert in text categorization and your job is to take a given activity label and add one of given
    locations to it. The given locations are 'Home', 'Hospital' and 'Doctors'. If it is unclear, where the person is,
    please use 'Home'. Furthermore it is really important, that that location is correct.
    The only output should be the location.
"""

LOCATION_PROMPT = """
    Explain step by step your conclusions your choice of location: 'Home' or 'Hospital' or 'Doctors' or 'Other'.
    Here is the activity label for which you should extract the location:
"""

LOCATION_ANSWER = """
    For example for the activity label 'visiting doctor's', you should return 'Doctors'. For the point
    'testing positive for Covid19', you also should return 'Doctors'.
    For 'getting hospitalized' the output is 'Hospital'.
"""

FC_LOCATION_CONTEXT = """
    You are an expert in extracting information.
    You easily detect locations and extract them as they are without changing any format.
    The only possible locations are 'Home', 'Hospital', 'Doctors' and 'Other'.
"""

FC_LOCATION_PROMPT = """
    Please extract the following location of the text without changing the given format:
"""
