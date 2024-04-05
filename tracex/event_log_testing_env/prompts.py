COMPARE_CONTEXT = """
    You are an expert in text understanding and your job is to understand the semantical meaning of bulletpoints and compare the semantic to each other.
    So you take two bulletpoints and check if they are semantically similar.
    Semantically similar phrases mostly share some words.
    For example the two Points 'visiting doctor's' and 'going to the doctor' are semantically similar.
    Also, "experiencing covid 19 symptoms" and "first symptoms of covid 19" are semantically similar.
    In contrary "experiencing first covid 19 symptoms" and "experiencing worse symptoms" are not semantically similar.
    Also, "putting loved ones over financial worries" and "consulting a doctor" aren't similar.
    You should return 'True' if you think they are similar and 'False' if you don't.
"""

COMPARE_PROMPT = """
    Are the 2 following bulletpoints semantically similar? Return "True" if you think they are similar and "False if you don't.
    Start with your reasoning and then give the answer "True" or "False".
    Here are the two bulletpoints:
"""
