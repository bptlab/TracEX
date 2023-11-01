import random
import openai
import constants as c
openai.api_key=c.oaik

def createPJ_task_prompt():
    if random.randrange(2)==0:
        sex = "male"
    else: 
        sex = "female"
    output = "Imagine being a " + sex + " person from " + getCountry() + ", that was infected with Covid19. You had first symptoms on " + getDate() + "." # Here should follow living circumstances
    return output

def getCountry():
    message = [{"role": "user", "content": "Please give me one european country."}]
    country = openai.ChatCompletion.create(model=c.model, messages=message, max_tokens=50, temperature=0.6)
    return country.choices[0].message.content
def getDate():
    message = [{"role": "user", "content": "Please give me one date between 01/01/2020 and 01/09/2023."}]
    country = openai.ChatCompletion.create(model=c.model, messages=message, max_tokens=50, temperature=0.6)
    return country.choices[0].message.content
def getLifeCircumstances():
    None #WIP

createPJ_label_prompt = """
    Please outline the course of your covid19 infection, what you did (and when you did that) because of it and which doctors you may consulted. 
    Please give some information about the time, in a few cases directly as a date and in the other as something in the lines of 'in the next days', 'the week after that' or similar.
    Give your outline as a continous text.
    Also include if you later went for getting the newly released vaccine. Do not include deails about who you are. 
"""

convertTtoBP_task_prompt = """
    Imagine you are a labeling expert and your job is to interpret a given text into events. 
    An event is a short description (maxmimum of 4 words) of what happens, followed by a timestamp (a date) with start and ending. 
    For example the sentence ' On April 1, 2020, I started experiencing mild symptoms such as a persistent cough, fatigue, and a low-grade fever.' 
    should be interpreted as 'experiencing mild symptoms (01/04/2020 - 01/04/2020)'. If there is no date given, try to receive it from the context. 
    You have to make sure, that a date is captured as a start and end date (i.e. '(01/04/2020 - 01/04/2020)') 
    For example if the first event happened on May 1 and the next event happened two weeks after that, the time stamp for the second event should be May 15. 
    Something like 'the following days' should be interpreted as the previous date until 2 days after (when the previous date was June 2, then this should be (02/06/2020 - 04/06/2020). 
    This should also apply on months and years! As example when someone mentions the following months and the preious timestamp was ending on October 3 the next should be (03/10/2020 - 03/12/2020).
    If there is absolutely no indiation of a date, please note that by stating 'date unknown' as timestamp. 
    Give out all events as bullet points and each in a new row.
    If there is some sort of ending summary, don't include that as a bullet.
"""

convertTtoBP_label_prompt = """
    Here is the text from which you should extract events: 
"""

convertBPtoA_task_prompt = """
    You are an expert activity label tagger system. 
    Your task is to accept activity labels such as 'create purchase order (April 1 - Apil 12)' as input and provide a list of tuples, where each one consists of the main action, the object it is applied on and a given start and end date. 
    For 'create purchase order (April 1 - Apil 12)', you would return (create, purchase order, April 1, April 12) and for 'purchase order (April 1 - Apil 12)' (, purchase order, April 1, April 12). 
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
"""

convertBPtoA_label_prompt = """
    Here are the points from which you should extract activity tags: 
"""