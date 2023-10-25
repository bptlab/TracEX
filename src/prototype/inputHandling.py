import openai
import os
import csv
import constants as c
import prompts as p
openai.api_key = c.oaik 

def convertInpToCSV(input):
    print("Converting Data: started.", end='\r')
    bulletPoints = convertTextToBulletpoints(input)
    print("Converting Data: 50%     ", end='\r')
    actions = convertBulletpointsToActions(bulletPoints)
    convertActionsToCSV(actions)
    print("Converting Data: Done.")

def convertTextToBulletpoints(input):
    messages = [
        {"role": "system", "content": p.convertTtoBP_task_prompt}, 
        {"role": "user", "content": p.convertTtoBP_label_prompt + input}
    ]
    bulletpoints = openai.ChatCompletion.create(model=c.model, messages=messages, max_tokens=c.maxtokens, temperature=0)
    return bulletpoints.choices[0].message.content

def convertBulletpointsToActions(bulletPoints):
    messages = [
        {"role": "system", "content": p.convertBPtoA_task_prompt}, 
        {"role": "user", "content": p.convertBPtoA_label_prompt + bulletPoints}
    ]
    actions = openai.ChatCompletion.create(model=c.model, messages=messages, max_tokens=c.maxtokens, temperature=0)
    return actions.choices[0].message.content

def convertActionsToCSV(actions):
    txt = actions.strip('[')
    txt = txt.strip(']')
    action_list = txt.split("\n")
    action_mat = []
    for entry in action_list:
        entry = entry.strip('(')
        entry = entry.rstrip('), ')
        entry = entry.split(", ")
        action_mat.append(entry) 
    fields = ['caseID', 'activity', 'object', 'start', 'end'] 
    with open(os.path.join(c.out_path, "output.csv"), 'w') as f:
        write = csv.writer(f)
        #write.writerow(['sep=,'])
        write.writerow(fields)
        for row_l in action_mat:
            if row_l != 1:
                row_l.insert(0,1)
                write.writerow(row_l)