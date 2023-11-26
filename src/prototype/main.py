"""Module providing the main function."""
import input_inquiry as ii
import input_handling as ih
import output_handling as oh

ii.greeting()
inp_txt = ii.get_input()
ih.convert_text_to_csv(inp_txt)
oh.get_output()
oh.farewell()
