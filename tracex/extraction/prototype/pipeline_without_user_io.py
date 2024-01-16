"""Module to run the pipeline without user interaction."""
import input_inquiry as ii
import input_handling as ih
import output_handling as oh
import utils as u


# This will not be called anymore
def run_pipeline():
    """Runs the pipeline without user interaction."""
    input_text = ii.create_patient_journey()
    u.pause_between_queries()
    ih.convert_text_to_csv(input_text)
    oh.get_output_without_user_io()


REPS = 1
for i in range(REPS):
    print(str(i + 1) + "/" + str(REPS))
    run_pipeline()
