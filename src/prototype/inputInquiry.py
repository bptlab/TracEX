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
    awnser = input("Would you like to continue with an existing patient journey as .txt? (y/n)\n").lower()
    if awnser == "y":
        filename = input("Please enter the name of the .txt file (located in 'content/inputs/'):\n")
        if filename[-4:] != ".txt":
            filename += ".txt"
        if not os.path.isfile(os.path.join(c.in_path, filename)):
            print('File does not exist.')
            return getInputPath()
        else:
            return filename
    if awnser == "n":
        return "new"
    else:
        print("Please enter y or n.")
        return getInputPath()
    
def createPJ():
    print("Please wait while the system is generating a patient journey. This may take a few moments.")
    messages = [
        {"role": "system", "content": p.createPJ_context()}, 
        {"role": "user", "content": p.createPJ_prompt}
    ]
    patient_journey = openai.ChatCompletion.create(model=c.model, messages=messages, max_tokens=c.maxtokens, temperature=0.5)
    patient_journey_txt = patient_journey.choices[0].message.content
    i = 0
    proposed_filename = "syntheticPatientJourney"+str(i)+".txt"
    output_path = os.path.join(c.in_path, proposed_filename)
    while os.path.isfile(output_path):
        i += 1
        proposed_filename = "syntheticPatientJourney"+str(i)+".txt"
        output_path = os.path.join(c.in_path, proposed_filename)
    with open(output_path, 'w') as f:
        f.write(patient_journey_txt)
    print("Patient journey \"" + proposed_filename + "\" generated.")
    return patient_journey_txt
