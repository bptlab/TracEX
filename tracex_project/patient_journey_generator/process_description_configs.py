PATIENT_JOURNEY_CONFIG = {
    "domain": "patient journeys",
    "case": "Patient",
    "case_notion": "Hospital Stay",
    "event_types": "Symptom Onset, Hospital Admission, Treatment",
    "case_attributes_dict": {
        "age": 24,
        "sex": "female",
        "occupation": "flight attendant",
        "origin": "France",
        "condition": "limp",
        "preexisting_conditions": "none"
    },
    "time_specifications": "timestamps and durations",
    "writing_style": "similar_to_example",
    "example": "I was admitted to the hospital on 01/01/2020. After a week, I was discharged. I was prescribed medication for the next two weeks.",
    "perspective_instructions": "Write the process description from the perspective of the Patient and consider the case attributes.",
    "writing_instructions": "Please create a process description in the form of a written text of your case. It is important that you write an authentic, continuous text, as if written by the Patient themselves.",
    "authenticity_instructions": "Please try to consider the Patient's background and the events that plausibly could have happened to them when creating the process description and the events that they experienced."
}


PATIENT_JOURNEY_CONFIG_MC = {
    "domain": "patient journeys",
    "case": "Patient",
    "case_notion": "Symptom Onset to Symptom Offset",
    "event_types": ["Symptom Onset", "Symptom Offset", "Diagnosis", "Doctor Visit", "Treatment", "Hospital Admission", "Hospital Discharge", "Medication", "Lifestyle Change", "Feelings"],
    "case_attributes_dict": {
        "age": [18, 20, 22, 25, 28, 30, 32, 35, 38, 40, 42, 45, 48, 50, 52, 55, 58, 60, 62, 65],
        "sex": ["male", "female"],
        "occupation": ["flight attendant", "teacher", "engineer", "chef", "artist", "musician", "nurse", "journalist", "software developer", "farmer", "scientist", "lawyer", "salesperson", "mechanic", "pilot", "police officer", "fitness instructor", "librarian", "architect", "politician"],
        "domestic_status": ["single", "married", "divorced", "widowed", "in a relationship"],
        "origin": ["France", "Germany", "Spain", "Italy", "Portugal", "Belgium", "Netherlands", "Switzerland", "Austria", "Sweden", "Norway", "Denmark", "Finland", "Poland", "Czech Republic", "Slovakia", "Hungary", "Romania", "Bulgaria", "Greece"],
        "condition": ["Covid-19", "asthma", "diabetes type 1", "diabetes type 2", "chronic kidney disease", "coronary artery disease", "stroke", "hypertension", "arthritis", "osteoporosis", "chronic obstructive pulmonary disease", "anxiety disorder", "depressive disorder", "bipolar disorder", "schizophrenia", "autism spectrum disorder", "dementia", "Parkinson's disease", "multiple sclerosis", "muscular dystrophy", "cystic fibrosis"],
        "preexisting_conditions": ["none", "diabetes", "asthma", "hypertension", "cardiovascular disease", "arthritis", "chronic kidney disease", "depression", "anxiety disorder", "obesity", "thyroid disorder", "cancer", "COPD", "migraines", "allergies", "eczema", "HIV/AIDS", "Parkinson's disease", "multiple sclerosis", "epilepsy"]
    },
    "time_specifications": ["timestamps and durations", "timestamps", "durations", "none"],
    "writing_style": "similar_to_example",
    "example": [
        "I was admitted to the hospital on 01/01/2020. After a week, I was discharged. I was prescribed medication for the next two weeks.",
        "I started feeling sick on 01/01/2020. I went to the hospital and was admitted. After a week, I was discharged and given medication to take for two weeks.",
        "It was my first ever COVID infection, the likelihood of hospitalization were high. I Am a obese 26yo male, "
        "with underlying health conditions and a disabillty. the first 4 days were pure hell that i hope no one has "
        "to go through, the cough was so dry and bad, it was almost like i was a patient in a old care home with "
        "tuberculosis, that is just how bad it was. The fever, chills, constant need to turn the heating on and off, "
        "grimacing in severe body aches and pain. i just wanted it to end. Finally after day 9 i am feeling like "
        "myself and LONG COVID seems unlikely as all my symptoms are gone besides some lingering myalgia and "
        "dehydration upon waking. I am scheduling for another booster and flu shot next week so i dont have to go "
        "through this again. I live in Australia btw.",
    ],
    "perspective_instructions": "Write the process description from the perspective of the Patient and consider their case attributes.",
    "writing_instructions": "Please create a process description in the form of a written text of your case. It is important that you write an authentic, continuous text, as if written by the Patient themselves.",
    "authenticity_instructions": "Please try to consider the Patient's background and the events that plausibly could have happened to them when creating the process description and the events that they experienced."
}  # verteile case attributes über ganze description


ORDER_CONFIG = {
    "domain": "retail orders",
    "case": "Product",
    "case_notion": "Order",
    "event_types": "Order Creation, Order Payment, Order Delivery",
    "case_attributes_dict": {
        "product_type": "smartphone",
        "model": "iPhone 13",
        "color": "red",
        "price": 999,
        "payment_method": "credit card",
        "retailer": "Apple Store",
        "delivery_address": "1234 Elm Street",
        "delivery_date": "01/01/2022"
    },
    "time_specifications": "timestamps and durations",
    "writing_style": "not_similar_to_example",
    "example": "I ordered a smartphone on 01/01/2022. I paid for it with my credit card. The smartphone was delivered to my address on 01/02/2022.",
    "perspective_instructions": "Write the process description from the perspective of an omniscient observer of the ordering process and consider the case attributes.",
    "writing_instructions": "Please create a process description in the form of a written text of your case. It is important that you write an authentic, continuous text.",
    "authenticity_instructions": "Please try to consider the aspects that this process might entail and include all parties that might be involved in this process and the activities that plausibly could have happened when creating the process description and the events that might have happened."
}