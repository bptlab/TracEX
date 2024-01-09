TOOLS = [
        {
        "type": "function",
        "function": {
                "name": "add_start_dates",
                "description": "this function extract the start date",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "output": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "an start date",
                            }
                        },
                    },
                    "required": ["output"]
                },
        }
    },
    {
        "type": "function",
        "function": {
                "name": "add_end_dates",
                "description": "this function extract the end date",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "output": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "an end date",
                            }
                        },
                    },
                    "required": ["output"]
                },
        }
    },
]