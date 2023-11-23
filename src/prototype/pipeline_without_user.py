"""Module to run the pipeline without user interaction."""
import time
import input_inquiry as ii
import input_handling as ih
import output_handling as oh


def run_pipeline():
    """Runs the pipeline without user interaction."""
    inp, inp_file_name = ii.create_patient_journey()
    time.sleep(5)
    ih.convert_inp_to_csv(inp)
    oh.get_output_without_user(inp_file_name)


reps = 2
for i in range(reps):
    print(i + "/" + reps)
    run_pipeline()
