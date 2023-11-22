import input_handling as ih
import output_handling as oh
import utils as u

inp = open("content/outputs/intermediates/6_bulletpoints_with_location.txt", "r").read()
ih.convert_bulletpoints_to_csv(inp)
ih.convert_csv_to_xes(u.CSV_OUTPUT)

oh.get_output("journey_synth_covid_0.txt")
