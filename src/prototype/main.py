import os
import pm4py
import openai
import csv
import pandas as pd 

import constants as c
import inputInquiry as ii
import inputHandling as ih 

inp = ii.getInput()
ih.convertInpToCSV(inp)
