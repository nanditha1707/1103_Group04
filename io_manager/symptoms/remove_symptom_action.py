from typing import override

from io_manager import messages
from io_manager.console.console import Console
from io_manager.symptoms.symptom_menu_action import SymptomMenuAction


class RemoveSymptomAction(SymptomMenuAction):
    """
    Shows current symptoms and removes the one the patient inputs,
    or every symptom if they type ALL.
    """

    # Sets what the user can type to remove all symptoms at once.
    REMOVE_ALL = "ALL"

    def __init__(self) -> None:
        super().__init__(messages.REMOVE_SYMPTOM_LABEL)

    @override
    def execute(self, console: Console, symptoms: list[str]) -> bool:
        # Checks if there are any symptoms to remove, 
        # and shows an error message if there are no current symptoms.
        if not symptoms:
            console.show(messages.NO_SYMPTOMS_TO_REMOVE)
            return False

        console.show(messages.CURRENT_SYMPTOMS.format(symptoms=", ".join(symptoms)))
        # Prompts the user to input a symptom to remove, or ALL to remove all symptoms.
        prompt = messages.REMOVE_SYMPTOM_PROMPT.format(remove_all=self.REMOVE_ALL)
        target = console.ask(prompt).strip().upper()

        # Check if the user input is empty,
        # and show an error message if so.
        if not target:
            console.show(messages.EMPTY_INPUT_ERROR)
        # Check if the user wants to remove all symptoms, 
        # and clear the list if so.
        elif target == self.REMOVE_ALL:
            symptoms.clear()
            console.show(messages.ALL_SYMPTOMS_REMOVED)
        # Check if the user input is in the list of symptoms,
        # and remove it if so.
        elif target in symptoms:
            symptoms.remove(target)
        else:
            # Show an error message if the user input is not in the list of symptoms.
            console.show(messages.SYMPTOM_NOT_IN_LIST.format(symptom=target))

        # Ensures menu keeps running.
        return False
