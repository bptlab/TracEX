import constants as c
import os
import openai
openai.api_key = c.oaik

print(os.environ.get("OPENAI_API_KEY"))