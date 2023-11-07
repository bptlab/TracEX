import os
import openai
import pandas as pd
import pm4py
import csv

import constants as c
import prompts as p
import inputInquiry as ii
import inputHandling as ih
import outputHandling as oh
openai.api_key = c.oaik

### JUST FOR TESTING, NO RELEVANCE FOR TRACEX! IMPLEMENTATION SHOULDN'T BE INCLUDED ON MAIN BRANCH! ###

inp = open("content/outputs/intermediates/bulletpoints.txt", "r").read()
bp = ih.addEndingCommas(inp)
print(bp)


#print("Hello World")