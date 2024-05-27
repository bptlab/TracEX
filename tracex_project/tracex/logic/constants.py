"""
Provide constants for the project.

Constant Numbers:
MAX_TOKENS -- Maximum number of tokens allowed for a single OpenAI API request.
MODEL -- Model to use for the OpenAI API requests.
OAIK -- OpenAI API Key retrieved from the environment variables.
TEMPERATURE_SUMMARIZING -- Temperature parameter for the OpenAI API requests for summarization tasks.
TEMPERATURE_CREATION -- Temperature parameter for the OpenAI API requests for creation tasks.
THRESHOLD_FOR_MATCH -- Threshold for the similarity score to consider a match. Similarity score range from 0 to 1.

Constant Lists:
ACTIVITY_KEYS -- List of tuples of possible activity keys for renaming and ordering a directly-follows-graph.
EVENT_TYPES -- List of possible event types for an activity.
EUROPEAN_COUNTRIES -- List of European countries.
LOCATIONS -- List of tuples of possible locations for an activity.
MODULES_OPTIONAL -- List of tuples of optional modules for the trace extraction process.
MODULES_REQUIRED -- List of tuples of required modules for the trace extraction process.
Note: The tuples in the lists contain the key, that is used in the code, and the value, that is displayed to the user.
"""
import os
from typing import Final

# Constant Numbers
MAX_TOKENS: Final = 1100
MODEL: Final = "gpt-3.5-turbo"
OAIK: Final = os.environ.get("OPENAI_API_KEY")
TEMPERATURE_SUMMARIZING: Final = 0
TEMPERATURE_CREATION: Final = 1
THRESHOLD_FOR_MATCH: Final = 0.5

# Constant Lists
ACTIVITY_KEYS: Final = [
    ("event_type", "Event Type"),
    ("activity", "Activity Label"),
    ("attribute_location", "Location"),
]
EVENT_TYPES: Final = [
    ("Symptom Onset", "Symptom Onset"),
    ("Symptom Offset", "Symptom Offset"),
    ("Diagnosis", "Diagnosis"),
    ("Doctor Visit", "Doctor Visit"),
    ("Treatment", "Treatment"),
    ("Hospital Admission", "Hospital Admission"),
    ("Hospital Discharge", "Hospital Discharge"),
    ("Medication", "Medication"),
    ("Lifestyle Change", "Lifestyle Change"),
    ("Feelings", "Feelings"),
    ("N/A", "N/A"),
]
EUROPEAN_COUNTRIES: Final = [
    "Albania",
    "Andorra",
    "Armenia",
    "Austria",
    "Azerbaijan",
    "Belarus",
    "Belgium",
    "Bosnia and Herzegovina",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Estonia",
    "Faroe Islands",
    "Finland",
    "France",
    "Georgia",
    "Germany",
    "Greece",
    "Hungary",
    "Iceland",
    "Ireland",
    "Italy",
    "Kazakhstan",
    "Kosovo",
    "Latvia",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Moldova",
    "Monaco",
    "Montenegro",
    "Netherlands",
    "North Macedonia",
    "Norway",
    "Poland",
    "Portugal",
    "Romania",
    "Russia",
    "San Marino",
    "Serbia",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "Switzerland",
    "Turkey",
    "Ukraine",
    "United Kingdom (UK)",
    "Vatican City (Holy See)",
]
LOCATIONS: Final = [
    ("Home", "Home"),
    ("Hospital", "Hospital"),
    ("Doctors", "Doctors"),
    ("N/A", "N/A"),
]
MODULES_OPTIONAL: Final = [
    ("preprocessing", "Preprocessor"),
    ("time_extraction", "Time Extractor"),
    ("event_type_classification", "Event Type Classifier"),
    ("location_extraction", "Location Extractor"),
    ("metrics_analyzer", "Metrics Analyzer"),
]
MODULES_REQUIRED: Final = [
    ("activity_labeling", "Activity Labeler"),
    ("cohort_tagging", "Cohort Tagger")
]
SNOMED_CT_API_URL = (
    "https://browser.ihtsdotools.org/snowstorm/snomed-ct/browser/MAIN/descriptions"
)
SNOMED_CT_PARAMS = params = {
    "limit": 1,
    "conceptActive": "true",
    "lang": "english",
    "skipTo": 0,
    "returnLimit": 1,
}
SNOMED_CT_HEADERS = {
    "User-Agent": "browser",
}
