# pylint: disable=line-too-long
"""Module providing functions for using OpenAI function calling."""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_start",
            "description": "this function extracts the start date",
            "parameters": {
                "type": "object",
                "properties": {
                    "output": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "a date in the format YYYYMMDDT0000 and if not available N/A",
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
            "name": "add_end",
            "description": "this function extracts the end date",
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
            "description": "this function extracts the duration",
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
            "description": "this function extracts the event type",
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
            "description": "this function extracts the location",
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
