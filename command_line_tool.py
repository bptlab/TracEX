"""Module providing the main function."""
# pylint: disable=wrong-import-position
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tracex.tracex.settings")
# pylint: enable=wrong-import-position

from tracex.extraction.logic.orchestrator import Orchestrator, ExtractionConfiguration
from tracex.extraction.logic import utils as u


def main():
    """Main function calling every pipeline step needed to run the program."""
    config = ExtractionConfiguration()
    orchestrator_instance = Orchestrator(config)
    greeting()
    input_text = get_input(orchestrator_instance)
    config.update(patient_journey=input_text)
    orchestrator_instance.run()
    print("The pipeline has been executed successfully.\n")
    output_decision = u.get_decision("Would you like to see the output? (y/n)\n")
    if output_decision:
        print(orchestrator_instance.data)


def greeting():
    """Prints a greeting message."""
    print(
        "\n\nWelcome to the prototype of TracEX!\n-----------------------------------"
    )


def get_input(orchestrator_instance):
    """Gets the input from the user."""
    input_path = get_input_path()
    if input_path == "new":
        inp = orchestrator_instance.generate_patient_journey()
    else:
        with open((u.input_path / input_path)) as f:
            inp = f.read()
    return inp


def get_input_path():
    """Gets the path to the input file from the user."""
    answer = input(
        "Would you like to continue with an existing patient journey as .txt? (y/n)\n"
    ).lower()
    if answer == "y":
        return get_input_path_name()
    if answer == "n":
        return "new"
    print("Please enter y or n.")
    return get_input_path()


def get_input_path_name():
    """Gets the name of the input file from the user."""
    filename = input(
        "Please enter the name of the .txt file (located in 'content/inputs/'):\n"
    )
    if filename[-4:] != ".txt":
        filename += ".txt"
    if not os.path.isfile((u.input_path / filename)):
        print("File does not exist.")
        return get_input_path_name()
    return filename


if __name__ == "__main__":
    main()
