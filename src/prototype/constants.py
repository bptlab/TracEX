import os
import openai
from pathlib import Path 

out_path = Path("content/outputs/") #Path to the outputs-folder
in_path = Path("content/inputs/") #Path to the inputs-folder
oaik = os.environ.get("OPENAI_API_KEY")
maxtokens = 200
model = "gpt-3.5-turbo"