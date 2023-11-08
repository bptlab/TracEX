"""Module providing the main function."""
import input_inquiry as ii
import input_handling as ih
import output_handling as oh

ii.greeting()
inp = ii.get_input()
xesfile = ih.convert_inp_to_xes(inp)
oh.get_output(xesfile)
oh.farewell()
