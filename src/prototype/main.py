import inputInquiry as ii
import inputHandling as ih 
import pandas as pd
import constants as c

#Put OpenAI-key as environment variable "OPENAI_API_KEY" in your system

inp = ii.getInput()
ih.convertInpToCSV(inp)
