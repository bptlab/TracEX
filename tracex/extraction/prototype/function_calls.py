# pylint: disable=line-too-long
"""Module providing a functions for using OpenAI function calling."""
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
                            "description": "a start date in the format YYYYMMDDT0000",
                        },
                    },
                },
                "required": ["output"],
            },
        },
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
                            "description": "a end date in the format YYYYMMDDT0000",
                        },
                    },
                },
                "required": ["output"],
            },
        },
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
                            "description": "a duration in the format HHH:MM:SS or HH:MM:SS",
                        },
                    },
                },
                "required": ["output"],
            },
        },
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
                            "description": "an event type (one of 'Symptom Onset', 'Symptom Offset', 'Diagnosis', 'Doctor visit', 'Treatment', 'Hospital stay', 'Medication', 'Lifestyle Change' and 'Feelings')",
                        },
                    },
                },
                "required": ["output"],
            },
        },
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
                            "description": "a location (one of  'Home', 'Hospital', 'Doctors' and 'Other')",
                        },
                    },
                },
                "required": ["output"],
            },
        },
    },
]
