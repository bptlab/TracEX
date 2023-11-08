import os
import pm4py


def getOutput(xesfile):
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
        getOutput(xesfile)


def farewell():
    print("-----------------------------------\nThank you for using TracEX!\n\n")
