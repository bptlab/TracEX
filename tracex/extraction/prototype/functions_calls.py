FUNCTIONS = [
    {
        "name": "convert_text_to_bulletpoints",
        "description": "Converts relevants parts related to the courseF of the disease of the input text to bulletpoints.",
        "parameters": {
                "type": "object",
                "properties": {
                    "output": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "An extracted bullet point"
                        },
                        "description": "List of relvant bullet points"
                    }
                },
            "required": ["output"]
        }
    },
    # {
    #     "name": "add_start_dates",
    #     "description": "Append to every bulletpoint a start date based on the input text.",
    #     "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "output": {
    #                     "type": "array",
    #                     "items": {
    #                         "type": "string",
    #                         "description": "the updated bulletpoint with start date"
    #                     },
    #                     "description": "List updated bullet points with start date"
    #                 }
    #             },
    #         "required": ["output"]
    #     }
    # },
]
