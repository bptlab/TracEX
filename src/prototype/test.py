import constants as c
import openai
openai.api_key = c.oaik

def getLand():
    label_prompt_1 = "Please give me one european country"
    model = "gpt-3.5-turbo"
    messages_1 = [
        {"role": "user", "content": label_prompt_1} #tell the system, what you want from it
    ]
    outline = openai.ChatCompletion.create(model=model, messages=messages_1, max_tokens=50, temperature=0.6)
    outline_txt = outline.choices[0].message.content
    print(outline_txt)
    return outline_txt


output = "Imagine being a " + getLand() + " person from germany, that was infected with covid19. You had first symptoms on the 1st of april 2020."+\
        "You belong to the upper working class, live in a rented appartment, have no wife or kids."
print(output)