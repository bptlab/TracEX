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
                                "description": "a start date",
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
                                "description": "a end date",
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
                "name": "add_duration",
                "description": "this function extract the duration",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "output": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "a duration",
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
                "name": "add_event_type",
                "description": "this function extract the event type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "output": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "an event type",
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
                "name": "add_location",
                "description": "this function extract the location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "output": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "a location",
                            }
                        },
                    },
                    "required": ["output"]
                },
        }
    },
]