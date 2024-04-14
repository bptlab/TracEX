COMPARE_MESSAGES = [
    {
        "role": "system",
        "content": """ You are an expert in text understanding and your job is to understand the semantical meaning of
            bulletpoints and compare the semantic to each other. So you take two bulletpoints and check if they are
            semantically similar. You should return True if you think they are similar and False if you don't.""",
    },
    {
        "role": "user",
        "content": "First: receiving support from my children\nSecond: taking medicine",
    },
    {"role": "assistant", "content": "False"},
    {
        "role": "user",
        "content": "First: visiting doctor's\nSecond: going to the doctor",
    },
    {"role": "assistant", "content": "True"},
    {
        "role": "user",
        "content": "First: experiencing covid 19 symptoms\nSecond: first symptoms of covid 19",
    },
    {"role": "assistant", "content": "True"},
    {
        "role": "user",
        "content": "First: experiencing first covid 19 symptoms\nSecond: experiencing worse symptoms",
    },
    {"role": "assistant", "content": "False"},
    {
        "role": "user",
        "content": "First: putting loved ones over financial worries\nSecond: consulting a doctor",
    },
    {"role": "assistant", "content": "False"},
    {
        "role": "user",
        "content": "First: isolating myself\nSecond: beginning self isolation",
    },
    {"role": "assistant", "content": "True"},
    {
        "role": "user",
        "content": "First: informing family\nSecond: informing family about my condition",
    },
    {"role": "assistant", "content": "True"},
    {
        "role": "user",
        "content": "First: getting hospitalized\nSecond: consulting family physician",
    },
    {"role": "assistant", "content": "False"},
    {
        "role": "user",
        "content": "First: taking immediate action\nSecond: isolating myself",
    },
    {"role": "assistant", "content": "False"},
    {
        "role": "user",
        "content": "First: isolating at home\nSecond: experiencing first covid 19 symptoms",
    },
    {"role": "assistant", "content": "False"},
    {
        "role": "user",
        "content": "First: advised home quarantine and treatment\nSecond: consulting family physician",
    },
    {"role": "assistant", "content": "False"},
    {
        "role": "user",
        "content": "First: informing family about situation\nSecond: isolating myself",
    },
    {"role": "assistant", "content": "False"},
    {
        "role": "user",
        "content": "First: consulting family physician\nSecond: consulting doctor",
    },
    {"role": "assistant", "content": "True"},
    {"role": "user", "content": "First: isolating myself\nSecond: isolating at home"},
    {"role": "assistant", "content": "True"},
]
