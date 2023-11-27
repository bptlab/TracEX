"""Module providing the main function."""
import input_inquiry as ii
import input_handling as ih
import output_handling as oh


def main():
    ii.greeting()
    input_text = ii.get_input()
    ih.convert_text_to_csv(input_text)
    oh.get_output()
    oh.farewell()


main()
