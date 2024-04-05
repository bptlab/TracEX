"""File containing all prompts for the extraction logic."""

TXT_TO_ACTIVITY_CONTEXT = """
    You are a summarizing expert for diseases and your job is to summarize a given text into bullet points regarding all important points about the course of the disease.
    Every bullet point has to be a short description that must not longer than 4 words.
    Every information that is not important for the course of the disease should be discarded!
    The bulletpoints have to be kept in present continuous tense and should begin with a verb!
    You must not include any dates or information about the time and focus on the main aspects you want to convey.
    You should not take two actions in one bullet point, but rather split them into two.
    Do not put commas in the bulletpoints. Try not to include enumerations. If absolutely necessary use slashes for enumeration.
    Do not put any punctuation to the end of the bullet points.
"""

TXT_TO_ACTIVITY_PROMPT = """
    Here is the text from which you should extract bullet points:
"""

TXT_TO_ACTIVITY_ANSWER = """
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


START_CONTEXT = """
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

START_PROMPT = """
    Here is the text and the activity label for which you should extract the start date in the format YYYYMMDD with the
    postfix T0000!
    In case that you are not able to find a start date return the term "N/A".
    Only use the format YYYYMMDDTHHMM e.g. 20200401T0000!
    Explain step by step your conclusions if the date YYYYMMDDTHHMM is available or N/A.
"""

START_ANSWER = """
    For example for the text
    'On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever.
    Four days later I went to the doctor and got tested positive for Covid19. In June I got infected again.
    After that I had a back pain' and the activity label 'experiencing mild symptoms' you should return '20200401T0000'.
    If the activity label is 'testing positive for Covid19' you should return '20200405T0000'.
    The activity label 'getting infected again' has only specified the month therefore the day is always the first of
    month and should be returned as '20200601T0000'.Furthermore, the activity label 'having back pain' hasn't specified
    a date in the text and context, therefore the date ist 'N/A'.
"""

FC_START_CONTEXT = """
   You are an expert in extracting information. You easily detect the start dates in the format YYYYMMDD with the
   postfix 'T0000' and extract them as they are without changing any format.
"""

FC_START_PROMPT = """
    What is the start date of given activity label in the format YYYYMMDDT000 (e.g. 20200101T000).
    If no start date is available extract N/A.
"""


END_CONTEXT = """
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

END_PROMPT = """
    Here is the text and the activity label with the start date for which you should extract the end date in the format
    YYYYMMDD with the postfix T0000! In case that you are not able to find a end date return the term "N/A".
    Only use the format YYYYMMDDTHHMM e.g. 20200401T0000! Explain step by step your conclusions if the end date
    YYYYMMDDTHHMM is available, if not calculate the average time of the activity and add this on the start date
    resulting as the end date.
"""

END_ANSWER = """
    For example for the text 'Four days after the first april 2020 I went to the doctor and got tested positive for
    Covid19. I was then hospitalized for two weeks.' and the activity label 'visiting doctor's' with the
    start date '20200405T0000' you should only return '20200405T0000'. For the activity label
    'testing positive for Covid19' with the start date '20200405T0000' you should only return '20200405T0000'. For the
    activity label 'getting hospitalized' with the start date '20200405T0000' you should only return '20200419T0000'.

    The text 'In the next time I made sure to improve my mental well being.' and the activity label
    'improving mental well being' with the start date '20210610T0000', you should output '20210710T0000'.
"""

FC_END_CONTEXT = """
    You are an expert in extracting information. You easily detect the end dates in the format YYYYMMDD with the
    postfix 'T0000' and extract them as they are without changing any format.
"""

FC_END_PROMPT = """
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

METRIC_ACTIVITY_CONTEXT = """
    You are an expert in text categorization and your job is to take given bulletpoint and to add one of the given relevance categories to every bulletpoint.
    The categories are as follows: No Relevance, Low Relevance, Moderate Relevance, High Relevance.
    It is important, that every bulletpoint gets a relevance category.
    Furthermore it is really important, that that relevance category is correct.
    The only output should be the relevance category and the reason why the bulletpoint is part of the category.
    Please do not add a phrase like "here are your bulletpoints" or something like that.

    The relevance categories are defined as follows:
    No Relevance: Events or actions that are not connected to the progression or impact of the disease of the patient in any way.
    Low Relevance: Events or actions that have limited potential to affect the progression of the disease of the patient and hold minimal significance in its course.
    Moderate Relevance: Events or actions that possess some potential to influence the disease's progression of the patient but may not be critical to its outcome.
    High Relevance: Events or actions that hold substantial potential to impact the disease's course of the patient and are crucial in understanding its trajectory.
"""

METRIC_ACTIVITY_PROMPT = """
    Please classify to given bulletpoint one of the following categories: No Relevance, Low Relevance, Moderate Relevance, High Relevance.
    Think step by step and derive from the bulletpoint the according category. Explain why a bulletpoint is assigned to a category in following template.
    Don't forget to include the reason why the bulletpoint is part of the category and don't repeat the bulletpoint in the answer.

    Take this as an example:
    Bulletpoint: 'receiving support from my children' -> Answer: 'Low Relvance: Receiving support from the childern is good for mental stability but have a low relevance for the course of disease.'
    Bulletpoint: 'taking medicine' -> Answer: 'High Relvance: Taking medicine is highly relevant for the course of the event. The medicine could help the patient to improve their health.'
    Bullepoint:  'eating chips' -> Answer: 'No Relevance: The action of eating chips has no direct or indirect impact on the course of the disease.'

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

COHORT_TAG_MESSAGES = [
    [
        "condition",
        {
            "role": "system",
            "content": "You are an expert in text understanding and your job is to take a given text about an illness \
            and to extract the illness it is about.",
        },
        {
            "role": "user",
            "content": "In July I got infected with Covid-19 which resulted in similar symptoms like a heavy flu.",
        },
        {"role": "assistant", "content": "Covid-19"},
        {"role": "user", "content": "I had a heavy flu in July."},
        {"role": "assistant", "content": "Flu"},
        {
            "role": "user",
            "content": "Last year I was feeling really well, when all of a sudden I had severe breathtaking problems \
            and high fever. I thought it was a flu, but it turned out to be Covid-19.",
        },
        {"role": "assistant", "content": "Covid-19"},
    ],
    [
        "gender",
        {
            "role": "system",
            "content": "You are an expert in text understanding and your job is to take a given text about an illness \
            and to extract the gender of the author. If the gender isn't clear, you should take the context into \
            account. Only if the context doesn't help, you should return 'N/A'.",
        },
        {
            "role": "user",
            "content": "I am a 25 year old software engineer living in California with my girlfriend. When I got \
            Covid-19 last year I was really worried about my job and my girlfriend.",
        },
        {"role": "assistant", "content": "male"},
        {
            "role": "user",
            "content": "I am a nurse living in Berlin with my boyfriend. When I got Covid-19 last year I was really \
            worried about my job and my boyfriend.",
        },
        {"role": "assistant", "content": "female"},
        {
            "role": "user",
            "content": "I got Covid-19 last year and I was really worried about my job. The diesease itself wasn't \
            even that hard but it stressed me out, that I wasn't allowed to go to my job!",
        },
        {"role": "assistant", "content": "N/A"},
        {
            "role": "user",
            "content": "I am a 25 year old software engineer living in California with my girlfriend. When I got \
            Covid-19 that struck me as a mother of two really heavily.",
        },
        {"role": "assistant", "content": "female"},
        {
            "role": "user",
            "content": "I am a nurse living in Berlin. When I got Covid-19 I had to stay home what really hit me. \
            As a divorced father I only see my boy once every month and now I couldn't even do that.",
        },
        {"role": "assistant", "content": "male"},
    ],
    [
        "age",
        {
            "role": "system",
            "content": "You are an expert in text understanding and your job is to take a given text about an illness \
                and to extract the age of the author. If the gender isn't clear, you should take the context into \
                    account. Young means 25, middle aged 50 and old 75. Only if the context doesn't help, you should \
                        return 'N/A'.",
        },
        {
            "role": "user",
            "content": "I am a 22 year old software engineer living in California with my girlfriend. When I got \
                Covid-19 last year I was really worried about my job and my girlfriend.",
        },
        {"role": "assistant", "content": "22"},
        {
            "role": "user",
            "content": "I am a nurse living in Berlin. When I got Covid-19 I had to stay home what really hit me. \
                Luckily as a young person I recovered quickly.",
        },
        {"role": "assistant", "content": "25"},
        {
            "role": "user",
            "content": "I got Covid-19 last year and I was really worried about my job. The diesease itself wasn't \
                even that hard but it stressed me out, that I wasn't allowed to go to my job!",
        },
        {"role": "assistant", "content": "N/A"},
        {
            "role": "user",
            "content": "I am an old man, so Covid-19 wasn't all easy on me.",
        },
        {"role": "assistant", "content": "75"},
    ],
    [
        "origin",
        {
            "role": "system",
            "content": "You are an expert in text understanding and your job is to take a given text about an illness \
                  and to extract the origin country of the author. If the origin isn't clear, you should take the \
                    context into account. Only if the context doesn't help, you should return 'N/A'.",
        },
        {
            "role": "user",
            "content": "I am a 25 year old software engineer living in California with my girlfriend. When I got \
                Covid-19 last year I was really worried about my job and my girlfriend.",
        },
        {"role": "assistant", "content": "United States of America"},
        {
            "role": "user",
            "content": "I am a nurse living in Berlin. When I got Covid-19 I had to stay home what really hit me. \
                Luckily as a young person I recovered quickly.",
        },
        {"role": "assistant", "content": "Germany"},
        {
            "role": "user",
            "content": "I got Covid-19 last year and I was really worried about my job. The diesease itself wasn't \
                even that hard but it stressed me out, that I wasn't allowed to go to my job!",
        },
        {"role": "assistant", "content": "N/A"},
    ],
    [
        "preexisting_condition",
        {
            "role": "system",
            "content": "You are an expert in text understanding and your job is to take a given text about an illness \
                and to extract previous diseases of the author. These diseases have to be EXPLICITLY MENTIONED. \
                    And they have to have occured BEFORE the illness the text is about!",
        },
        {
            "role": "user",
            "content": "I got Covid-19 last year, which was hard since I since ever had to fight Asthma.",
        },
        {"role": "assistant", "content": "Asthma"},
        {
            "role": "user",
            "content": "I infected me with Covid-19 right after I recovered from a heavy cold.",
        },
        {"role": "assistant", "content": "Cold"},
        {
            "role": "user",
            "content": "I got Covid-19 last year and I was really worried about my job. The diesease itself wasn't \
                even that hard but it stressed me out, that I wasn't allowed to go to my job!",
        },
        {"role": "assistant", "content": "N/A"},
        {
            "role": "user",
            "content": "I got Covid-19 last year after I already got it right at the start in 2020.",
        },
        {"role": "assistant", "content": "Covid-19"},
    ],
]

PREPROCESSING_SPELLCHECK = [
    {
        "role": "system",
        "content": "You are an expert in text analysis with a focus on spelling accuracy. \
            Your task is to identify any spelling errors in the provided text and correct them. \
            Ensure the corrected text is accurate and readable. \
            Please make sure to give out the full text without shorten it.",
    },
    {
        "role": "user",
        "content": "I remeber the day I first learnt about the importnce of spellchek. \
            It was an eye-opener for me.",
    },
    {
        "role": "assistant",
        "content": "I remember the day I first learned about the importance of spellcheck. \
            It was an eye-opener for me.",
    },
]

PREPROCESSING_PUNCTUATION = [
    {
        "role": "system",
        "content": "You are an expert in text analysis with a focus on grammatical accuracy, \
            specifically punctuation and comma usage. \
            Your task is to identify any punctuation or comma errors in the provided text and correct them. \
            Ensure the corrected text is accurate, readable, and follows standard punctuation rules. \
            Please make sure to give out the full text without shortening it.",
    },
    {
        "role": "user",
        "content": "Despite the rainy weather many people attended the outdoor concert, \
            which, was surprising. The band played hit after hit, and the crowd's enthusiasm, \
            was infectious even the most reserved attendees found themselves dancing.",
    },
    {
        "role": "assistant",
        "content": "Despite the rainy weather, many people attended the outdoor concert, \
            which was surprising. The band played hit after hit, and the crowd's enthusiasm was infectious;\
            even the most reserved attendees found themselves dancing.",
    },
]

PREPROCESSING_IDENTIFY_TIMESTAMPS = [
    {
        "role": "system",
        "content": "You are an expert in text analysis. \
            Your task is to identify and extract any timestamps (specific dates, months, years, recognized holidays, \
            timeframes like '12 weeks later', or periods between specific dates) mentioned in the context of an \
            individual experiencing symptoms or being diagnosed with an illness. Highlight these timestamps within \
            the text by surrounding them with $$$ symbols. Ensure the full text is presented without any omissions, \
            and only the timestamps are highlighted in this manner.",
    },
    {
        "role": "user",
        "content": "I started feeling unwell around the middle of March 2021. \
            The symptoms were quite severe by the 20th of March, which is when I decided to get tested. \
            The test results came back positive for Covid-19 on March 22nd, 2021.",
    },
    {
        "role": "assistant",
        "content": "I started feeling unwell around the middle of $$$March 2021$$$. \
            The symptoms were quite severe by the $$$20th of March$$$, which is when I decided to get tested. \
            The test results came back positive for Covid-19 on $$$March 22nd, 2021$$$.",
    },
    {
        "role": "user",
        "content": "I started feeling unusually fatigued right before Thanksgiving 2020. \
            The fatigue worsened over the holiday, and by the following Monday, I had developed a fever. \
            I was tested for Covid-19 $$$two days later$$$ and received a positive result on November 30th, 2020.",
    },
    {
        "role": "assistant",
        "content": "I started feeling unusually fatigued right before $$$Thanksgiving 2020$$$. \
            The fatigue worsened over the holiday, and by the following Monday, I had developed a fever. \
            I was tested for Covid-19 $$$two days later$$$ and received a positive result on $$$November 30th, 2020$$$.",
    },
]

PREPROCESSING_TRANSFORM_TIMESTAMPS = [
    {
        "role": "system",
        "content": "You are an expert in text analysis and date formatting. \
            Your task is to identify any timestamps related to when an individual experienced symptoms \
            or was diagnosed with an illness. \
            Convert and present these timestamps in the specific format of YYYY/MM/DD. \
            All relevant time specifications are already highlighted with $$$ $$$. \
            To guarantee the completeness of the date you must make assumptions about the year, month and day \
            based on the context. If the time specification is a duration, based on context, \
            you must make assumptions about the start date of the duration. \
            If there is no information about the year, month or day, \
            you are allowed to assume the current year, month or day. \
            Ensure the full text is presented without any omissions, \
            and try to transform every timestamps as concrete as possible. \
            Please make sure to give out the full text without shortening it.",
    },
    {
        "role": "user",
        "content": "I noticed the first symptoms shortly after my birthday in $$$April$$$, \
            and exactly $$$12 weeks later$$$, my condition had deteriorated significantly. \
            I was officially diagnosed with Lyme disease on $$$August 7th$$$.",
    },
    {
        "role": "assistant",
        "content": "I noticed the first symptoms shortly after my birthday on 2024/04/01, \
            and exactly 12 weeks later, on 2024/06/24, my condition had deteriorated significantly. \
            I was officially diagnosed with Lyme disease on 2024/08/07.",
    },
    {
        "role": "user",
        "content": "During the period between $$$the 01.02 and the 03.02$$$, I felt unusually tired, \
            but I thought it was just stress. However, after attending a large event $$$two weeks later$$$, \
            I developed a fever and was tested positive for the flu.",
    },
    {
        "role": "assistant",
        "content": "During the period between 2024/02/01 and 2024/02/03, I felt unusually tired, \
            but I thought it was just stress. However, after attending a large event two weeks later, on 2024/02/17, \
            I developed a fever and was tested positive for the flu.",
    },
]

PREPROCESSING_TIME_CALCULATION = [
    {
        "role": "system",
        "content": "You are an expert in text analysis and date calculations. \
            Your task is to identify timestamps related to health events or diagnoses and \
            convert these into concrete dates in the format of YYYY/MM/DD. \
            For relative timestamps (like 'a few weeks after' or 'months before'), \
            calculate the exact dates based on provided or assumed known dates. \
            Ensure the text is complete without omission, with all relevant timestamps \
            accurately transformed to the specified format. \
            Please make sure to give out the full text without shortening it.",
    },
    {
        "role": "user",
        "content": "After experiencing severe headaches starting in mid-$$$March 2022$$$, \
            I went to see a neurologist. \
            The MRI scan scheduled $$$three weeks later$$$ confirmed that I had a benign brain tumor. \
            Post-surgery, I began my recovery phase, which lasted until $$$four months later$$$. \
            During a follow-up visit $$$two months after my recovery$$$, \
            my doctor confirmed that my condition had improved significantly.",
    },
    {
        "role": "assistant",
        "content": "After experiencing severe headaches starting on 2022/03/15, \
            I went to see a neurologist. The MRI scan scheduled on 2022/04/05 confirmed that I had a benign brain tumor.\
            Post-surgery, I began my recovery phase, which lasted until 2022/08/05. \
            During a follow-up visit on 2022/10/05, \
            my doctor confirmed that my condition had improved significantly.",
    },
    {
        "role": "user",
        "content": "Early July 2020, I started experiencing severe coughing and a high fever. \
            It turned out I had contracted Covid-19. And in $$$early August$$$ I had lost my sense of taste.",
    },
    {
        "role": "assistant",
        "content": "On the 2020/06/01, I started experiencing severe coughing and a high fever. \
            It turned out I had contracted Covid-19. And on 2020/08/01 I had lost my sense of taste.",
    },
]

PREPROCESSING_TIME_INTERPRETATION = [
    {
        "role": "system",
        "content": "You are an expert in text analysis with a specialization in date formatting \
            and interpretation. Your task is to transform general time references related to health events \
            or any other context into specific dates in the format of YYYY/MM/DD. Specifically, \
            convert 'early [month]' to the 1st of the month, 'mid [month]' to the 15th of the month, \
            and 'end of [month]' to the last day of the month (use 30 for April, June, September, \
            and November; 31 for January, March, May, July, August, October, and December; \
            and 28 or 29 for February, depending on leap years). \
            If the year is not mentioned, assume the current year. \
            Provide the full text without omission, ensuring all general time references are accurately \
            transformed into the specified format. \
            Example transformations: 'early January 2020' becomes 2020/01/01, \
            'mid January 2020' becomes 2020/01/15, and 'end of January 2020' becomes 2020/01/31.",
    },
    {
        "role": "user",
        "content": "In early January, I noticed a persistent cough. By mid January, the cough had worsened, \
            leading me to seek medical advice. A specialist finally saw me at the end of January, \
            diagnosing me with a chronic condition.",
    },
    {
        "role": "assistant",
        "content": "In 2020/01/01, I noticed a persistent cough. By 2020/01/15, the cough had worsened,\
             leading me to seek medical advice. A specialist finally saw me at 2020/01/31, \
             diagnosing me with a chronic condition.",
    },
]
