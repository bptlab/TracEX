TOOLS = [
    {
        "type": "function",
        "function": {
                "name": "add_start_dates",
                "description": "add to every bulletpoint the according a start date in the input text. The updated bullet point should only look like this 'experiencing mild symptoms, 20200401T0000'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "output": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "the updated bulletpoint with start date",
                            }
                        },
                    },
                    "required": ["output"]
                },
        }
    },
    

]


    # {
    #     "type": "function",
    #     "function": {
    #             "name": "convert_text_to_bulletpoints",
    #             "description": "Converts relevants parts related to the course of the disease of the input text to bulletpoints.",
    #             "parameters": {
    #                 "type": "object",
    #                 "properties": {
    #                     "output": {
    #                         "type": "array",
    #                         "items": {
    #                             "type": "string",
    #                             "description": "An extracted bullet point"
    #                         }
    #                     },
    #                 },
    #                 "required": ["output"]
    #             },
    #     }
    # },