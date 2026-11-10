from collections.abc import Sequence

from io_manager import messages
from io_manager.console.console import Console
from io_manager.navigation.navigation import Navigation
from io_manager.navigation.question_result import QuestionResult
from io_manager.rendering.box_renderer import BoxRenderer
from io_manager.symptoms.add_symptom_action import AddSymptomAction
from io_manager.symptoms.done_action import DoneAction
from io_manager.symptoms.remove_symptom_action import RemoveSymptomAction
from io_manager.symptoms.symptom_menu_action import SymptomMenuAction
from io_manager.validators.menu_option_validator import MenuOptionValidator

class SymptomMenu:
    """
    The numbered symptom menu shown for the symptoms question.
    Functions as a orchestration of the actions that can be performed on a list of symptoms.

    The different add symptom actions are parsed in first,
    The Remove and Done actions are created here and always come last in the order. 
    Menu numbers come dynamically from each other's position, 
    so adding an action needs no other change.
    """

    def __init__(
        self, add_actions: Sequence[AddSymptomAction], renderer: BoxRenderer
    ) -> None:
        # All actions are subclasses of SymptomMenuAction, 
        # so the type is a tuple of that.
        self.__actions: tuple[SymptomMenuAction, ...] = (
            # All the add actions come first, then the remove and done actions.
            *add_actions,
            RemoveSymptomAction(),
            DoneAction(),
        )
        self.__renderer = renderer
        # Creates the option validator for menu.
        self.__option_validator = MenuOptionValidator(
            maximum=len(self.__actions),
        )

    def run(self, console: Console, initial_symptoms: Sequence[str]) -> QuestionResult:
        """
        The menu runs in a loop until the patient picks Done, then returns the symptoms as an answer.

        Prints the menu, asks for an option, validates it, and executes the corresponding action.
        It works on a copy of initial_symptoms, 
        so typing back leaves the previous symptoms unchanged.
        """
        symptoms = list(initial_symptoms)
        menu = self.__renderer.render(self.__menu_lines(), messages.SYMPTOM_MENU_HEADER)

        while True:
            # Show the menu and ask for an option.
            console.show(menu)
            option = console.ask_normalised(messages.MENU_OPTION_PROMPT)

            result = QuestionResult.from_input(option, self.__option_validator)

            # If the option is invalid, show the error and continue the loop.
            if result.navigation is Navigation.INVALID:
                console.show(result.error)
                continue

            # BACK or QUIT is handed back to the question that runs the menu.
            if result.navigation is not Navigation.ANSWERED:
                return result

            # All options are one higher then the index of the action, 
            # so subtract 1 to get the index.
            action = self.__actions[int(option) - 1]
            # Execute the action, and if it returns True, 
            # return the symptoms as an answer.
            if action.execute(console, symptoms):
                return QuestionResult.answered(symptoms)

    def __menu_lines(self) -> list[str]:
        """
        Returns the lines of the menu, with the actions numbered and the hint at the end.
        """
        lines = [
            f"{number}. {action.label}"
            for number, action in enumerate(self.__actions, start=1)
        ]
        # The hint tells the user how to exit the menu
        lines.append(messages.SYMPTOM_MENU_HINT)
        return lines