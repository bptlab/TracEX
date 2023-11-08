"""Module providing the needed prompts for the gpt_queries"""
import random
import openai
import constants as c

openai.api_key = c.oaik


# Creation of a patient journey
def create_patient_journey_context():
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
        + lifeCircumstances
    )


def get_sex():
    if random.randrange(2) == 0:
        return "male"
    else:
        return "female"


def get_country():
    message = [{"role": "user", "content": "Please give me one european country."}]
    country = openai.ChatCompletion.create(
        model=c.MODEL, messages=message, max_tokens=50, temperature=0.2
    )
    return country.choices[0].message.content


def get_date():
    message = [
        {
            "role": "user",
            "content": "Please give me one date between 01/01/2020 and 01/09/2023.",
        }
    ]
    country = openai.ChatCompletion.create(
        model=c.MODEL, messages=message, max_tokens=50, temperature=0.5
    )
    return country.choices[0].message.content


def get_life_circumstances(sex):
    message = [{"role": "user", "content": lifeCircumstances_prompt(sex)}]
    life_circumstances = openai.ChatCompletion.create(
        model=c.MODEL, messages=message, max_tokens=100, temperature=1
    )
    return life_circumstances.choices[0].message.content


def life_circumstances_prompt(sex):
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


create_patient_journey_prompt = """
    Please outline the course of your covid19 infection, what you did (and when you did that) because of it and which doctors you may consulted.
    Please give some information about the time, in a few cases directly as a date and in the other as something in the lines of 'in the next days', 'the week after that' or similar.
    Give your outline as a continous text.
    Also include if you later went for getting a vaccine and if so, how often. You don't have to include deails about who you are.
    Please include 100 to 400 words, but not more than 400.
"""


# Conversion of a text to bullet points focused on the course of a disease
txt_to_bulletpoints_context = """
    You are a summarizing expert for diseases and your job is to summarize a given text into bullet points regarding all important points about the course of the disease.
    Every bullet point has to be a short description that is not longer than 4 words.
    Every information that is not important for the course of the disease should be discarded.
    The bulletpoints have to be kept in present continous tense and should begin with a verb!
    You must not include any dates or information about the time and focus on the main aspects you want to convey.
    You should not take two actions in one bullet point, but rather split them into two.
    Do not put commas in the bulletpoints. Try not to include enumerations. If absolutely necessary use slashes for enumeration.
    Do not put any punctuation to the end of the bullet points.
"""
txt_to_bulletpoints_prompt = """
    Here is the text from which you should extract bullet points:
"""
txt_to_bulletpoints_answer = """
    For example the text 'On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever.
    Four days later I went to the doctor and got tested positive for Covid19.' should be summarized as
    'experiencing mild symptoms, visiting doctor's, testing positive for Covid19'.
    The text 'Concerned about my condition, I contacted my primary care physician via phone. He advised me to monitor my symptoms and stay at home unless they became severe.'
    should be summarized as 'contacting primary care physician, monitoring symptoms at home'.
    Anything like 'the following days I waited for the symptoms to fade away' should be summarized as something like 'waiting for symptoms to subside'.
    'First symptoms on 01/04/2020' should be summarized as 'experiencing first symptoms'.
    'On July 15, 2022, I started experiencing the first symptoms of Covid-19. Initially, I had a mild cough and fatigue.' should be summarized as 'experiencing first symptoms'.
"""

"""
If a bullet point already contains any date information, delete that and only associated punctuation marks.
    Never remove ending commas at the end of a bulletpoint!
    Else d """

# Adding of a start date to every bullet point
bulletpoints_start_date_context = """
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
bulletpoints_start_date_prompt = """
    Here is the text and the bulletpoints for which you should extract start dates:
"""
bulletpoints_start_date_answer = """
    For example for the text 'On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever.
    Four days later I went to the doctor and got tested positive for Covid19.' and the bullet points
    '- experiencing mild symptoms,\n- visiting doctor's,\n- testing positive for Covid19,' you should return
    '- experiencing mild symptoms, 20200401T0000\n- visiting doctor's, 20200405T0000\n- testing positive for Covid19, 20200405T0000'.
    Accordingly for the same text and the bullet points '- experiencing first symptoms: 01/04/2020,\n- going to doctor four days later,\n- testing positive for Covid19,' you should return
    '- experiencing first symptoms, 20200401T0000\n- going to doctor, 20200405T0000\n- testing positive for Covid19, 20200405T0000'.
    If the text says 'A year after the vaccine was introduced, I got vaccined myself' and a bullet point says 'got vaccined',
    you should take online information about when a vaccine was introduced in the country the author is from into account and put that as start date.
    When the considered vaccine was introduced on 01/01/2021, you should return '- getting vaccined, 20220101T0000', as the author said, that he waited a year.
    If the text says something like "I got medication on the fith of july. Nevertheless my health wasn't improving in any way." and the bulletpoints are
    '- getting medication,\n- worsening health' you should return '- getting medication, 20200705T0000\n- worsening health, 20200705T0000'.
"""


# Adding of a end date to every bullet point
bulletpoints_end_date_context = """
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
bulletpoints_end_date_prompt = """
    Here is the text and the bulletpoints for which you should extract end dates:
"""
bulletpoints_end_date_answer = """
    For example for the text 'Four days after the first april 2020 I went to the doctor and got tested positive for Covid19. I was then hospitalized for two weeks.'
    and the bullet points '(visiting doctor's, 20200405T0000), (testing positive for Covid19, 20200405T0000), (getting hospitalized, 20200405T0000)' you should return
    '(visiting doctor's, 20200405T0000, 20200405T0000), (testing positive for Covid19, 20200405T0000, 20200405T0000), (getting hospitalized, 20200405T0000, 20200419T0000)'.
    The text 'In the next time I made sure to improve my mental wellbeing.' and the bulletpoint '(improving mental wellbeing, 20210610T0000)' could be updated to '(improving mental wellbeing, 20210610T0000, 20210710T0000)'.
"""

### --- OLD PROMPTS --- ###

# have to be rowrked, if usecase emerges! #
"""
convertBPtoA_task_prompt =
    You are an expert activity label tagger system.
    Your task is to accept activity labels such as 'create purchase order (01/04/2020 - 12/04/2020)' as input and provide a list of tuples, where each one consists of the main action, the object it is applied on and a given start and end date.
    For 'create purchase order (01/04/2020 - 12/04/2020)', you would return (create, purchase order, 20200401T0000, 20200412T0000) and for 'purchase order (01/04/2020 - 12/04/2020)' (, purchase order, 20200401T0000, 20200412T0000).
    That mean that if there is no clear main action extractable, just write nothing instead and just put a comma.
    If there is a year given, do not include that in the output!
    If actions are not provided as verbs, change them into verbs, e.g., for 'purchase order creation' you would hence return (create, purchase order) as well.
    Also turn past tense actions into present tense ones, e.g., 'purchase order created' becomes (create, purchase order) too.
    If multiple actions are applied to the same object, split this into multiple pairs, e.g., 'create and send purchase order' becomes (create, purchase order), (send, purchase oder)
    If there is additional information, e.g., about who is performing the action or about an IT system that is involved, discard that.
    If there are any special characters, just replace them with whitespace.

    Under no circumstances (!) put any other text in your answer, only a (possibly empty) list of pairs with nothing before or after.
    In each pair the (optional) action comes first, followed by the object (if any).
    If the activity label does not contain any actions, return an empty list , ie., []

convertBPtoA_label_prompt =
    Here are the points from which you should extract activity tags:
"""
