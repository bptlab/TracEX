"""Module to run the pipeline without user interaction."""
import time
import input_inquiry as ii
import input_handling as ih
import output_handling as oh


def run_pipeline():
    """Runs the pipeline without user interaction."""
    inp = ii.create_patient_journey()
    time.sleep(5)
    ih.convert_text_to_csv(inp)
    oh.get_output_without_user()


REPS = 1
for i in range(REPS):
    print(str(i + 1) + "/" + str(REPS))
    run_pipeline()
