import os
import openai

import constants as c
import prompts as p
openai.api_key = c.oaik

def getInput():
    print("Welcome to the prototype of TracEX!\n-----------------------------------")
    inputpath = getInputPath()
    if inputpath == "new":
        input = createPJ()
    else:  
        with open(os.path.join(c.in_path, inputpath)) as f:
            input = f.read()
    return input

def getInputPath():
    awnser = input("Would you like to continou with an existing patient journey as .txt? (y/n)\n").lower()
    if awnser == "y":
        filename = input("Please enter the name of the .txt file (located in 'content/inputs/'):\n")
        if filename[-4:] != ".txt":
            filename += ".txt"
        return filename
    if awnser == "n":
        return "new"
    else:
        print("Please enter y or n.")
        return getInputPath()
    
def createPJ():
    messages = [
        {"role": "system", "content": p.createPJ_task_prompt}, 
        {"role": "user", "content": p.createPJ_label_prompt}
    ]
    print("Please wait while the system is generating your patient journey. This may take a few moments.")
    patient_journey = openai.ChatCompletion.create(model=c.model, messages=messages, max_tokens=c.maxtokens, temperature=0.5)
    patient_journey_txt = patient_journey.choices[0].message.content
    print("Patient journey generated.")
    return patient_journey_txt