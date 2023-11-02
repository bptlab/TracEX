import inputInquiry as ii
import inputHandling as ih 
import pandas as pd
import constants as c
import os
import pm4py

#Put OpenAI-key as environment variable "OPENAI_API_KEY" in your system

inp = ii.getInput()
csvfile = ih.convertInpToCSV(inp)
ih.convertCSVToXES(csvfile)