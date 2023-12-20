"""Module providing the main function."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tracex.tracex.settings")

from tracex.extraction.prototype import input_inquiry as ii
from tracex.extraction.prototype import input_handling as ih
from tracex.extraction.prototype import output_handling as oh


def main():
    """Main function calling every pipeline step needed to run the program."""
    ii.greeting()
    input_text = ii.get_input()
    ih.convert_text_to_csv(input_text)
    oh.get_output()
    oh.farewell()


main()
