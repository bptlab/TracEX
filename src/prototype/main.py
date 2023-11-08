"""Module providing the main function."""
import input_inquiry as ii
import input_handling as ih
import output_handling as oh

ii.greeting()
inp = ii.getInput()
xesfile = ih.convertInpToXES(inp)
oh.get_output(xesfile)
oh.farewell()
