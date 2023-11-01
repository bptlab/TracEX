import constants as c
import os
import openai
import pandas as pd
import pm4py
openai.api_key = c.oaik

dataframe = pd.read_csv(os.path.join(c.out_path, "output.csv"), sep=',')
#print(dataframe)
dataframe = pm4py.format_dataframe(dataframe, case_id='caseID', activity_key='activity', timestamp_key='start')
print(dataframe)
pm4py.write_xes(dataframe, os.path.join(c.out_path, "test.xes"), case_id_key='case:concept:name')