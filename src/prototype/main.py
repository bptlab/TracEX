"""Module providing the main function."""
import input_inquiry as ii
import input_handling as ih
import output_handling as oh

ii.greeting()
inp = ii.get_input()
prompt_mode = ii.get_prompt_mode()
xesfile = ih.convert_inp_to_xes(inp, prompt_mode)
oh.get_output(xesfile)
oh.farewell()
