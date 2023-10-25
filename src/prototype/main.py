import os
import pm4py
import openai
import csv
import pandas as pd 

import constants as c
import inputInquiry as ii
import inputHandling as ih 

#Put openAI in "constants.py" and take it out of there before pushing to github!

inp = ii.getInput()
ih.convertInpToCSV(inp)
