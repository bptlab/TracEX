"""Module providing the main function."""
# pylint: disable=wrong-import-position
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tracex.tracex.settings")
# pylint: enable=wrong-import-position

from tracex.extraction.prototype import input_inquiry as ii
from tracex.extraction.prototype import input_handling as ih


def main():
    """Main function calling every pipeline step needed to run the program."""
    ii.greeting()
    input_text = ii.get_input()
    ih.convert_text_to_csv(input_text)


if __name__ == "__main__":
    main()
