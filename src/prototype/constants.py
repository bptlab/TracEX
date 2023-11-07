import os
from pathlib import Path 

out_path = Path("content/outputs/") #Path to the outputs-folder
in_path = Path("content/inputs/") #Path to the inputs-folder
oaik = os.environ.get("OPENAI_API_KEY") #Get the OpenAI API key from the environment variables
model = "gpt-3.5-turbo"
max_tokens = 600
temperature = 0.5