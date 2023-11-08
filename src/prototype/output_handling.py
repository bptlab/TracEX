# pylint: disable=import-error
"""Module providing functions for printing out the XES."""
import os

import pm4py


def get_output(xesfile):
    """Prints the output to the console or shows the filename."""
    if not os.path.isfile(xesfile):
        print("The output can not be read.")
        return
    decision = input("Would you like to see the output? (y/n)\n").lower()
    if decision == "y":
        print("Loading output...", end="\r")
        log = pm4py.read_xes(xesfile)
        df = pm4py.convert_to_dataframe(log)
        print(df)
    elif decision == "n":
        print("The output can be found at " + xesfile + ".")
    else:
        print("Please enter y or n.")
        get_output(xesfile)


def farewell():
    """Prints a farewell message."""
    print("-----------------------------------\nThank you for using TracEX!\n\n")
