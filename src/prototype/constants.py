import os
import openai
from pathlib import Path 

out_path = Path("content/outputs/") #Path to the outputs-folder
in_path = Path("content/inputs/") #Path to the inputs-folder
oaik = "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"
os.environ["OPENAI_API_KEY"] = oaik
maxtokens=200
model = "gpt-3.5-turbo"