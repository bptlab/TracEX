pj = ["awdasd", "asdawdasdaw", "lorem", "ipsum"]


patient_journey = pj
for count, value in enumerate(patient_journey):
    patient_journey[count] = str(count) + ": " + value
patient_journey = ".\n".join(patient_journey)

print(patient_journey)
