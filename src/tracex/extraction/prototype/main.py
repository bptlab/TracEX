"""Module providing the main function."""
from . import input_handling as ih
from . import input_inquiry as ii
from . import output_handling as oh

ii.greeting()
inp = ii.get_input()
xesfile = ih.convert_inp_to_xes(inp)
oh.get_output(xesfile)
oh.farewell()
