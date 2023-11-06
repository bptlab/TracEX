import constants as c
import os
import openai
import pandas as pd
import pm4py
import prompts as p
import inputInquiry as ii
import inputHandling as ih
import csv
openai.api_key = c.oaik

### JUST FOR TESTING, NO RELEVANCE FOR TRACEX! SHOULDNT BE INCLUDED ON MAIN BRANCH! ###

#ih.convertTextToBulletpoints(open("content/inputs/syntheticPatientJourney0.txt", "r").read())

#ih.convertCSVToXES("content/outputs/output.csv")


dataframe = pd.read_csv("content/outputs/output.csv", sep=',')
dataframe = dataframe.rename(columns={'event': 'Activity', 'start': 'date:StartDate', 'end': 'date:EndDate'})
dataframe = pm4py.format_dataframe(dataframe, case_id='caseID', activity_key='Activity', timestamp_key='date:StartDate')
pm4py.write_xes(dataframe, os.path.join(c.out_path, "output.xes"), case_id_key='case:concept:name')
""" 
print("Hello World") """