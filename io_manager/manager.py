from collections.abc import Mapping, Sequence

import pandas as pd

from io_manager import constants
from io_manager.console import Console
from io_manager.form import RegistrationForm
from io_manager.menus import NumberedOptions
from io_manager.navigation import Navigation
from io_manager.patient_answers import PatientAnswers
from io_manager.rendering import BoxRenderer, TableRenderer
from io_manager.screens import ConfirmationScreen, Questionnaire, ResultView
from io_manager.validators import DateValidator, MenuOptionValidator
from typedefs import Answer, Labelled


class IOManager:
    """
    The orchestrator class main.py uses for all input and output.

    IOManagerFactory builds every object it needs and passes them in through the constructor.
    It creates none of them itself so a test can pass in its own console or screens
    and a new front end or clinic setup needs no change to this class.
    """

    def __init__(
        self, console: Console, form: RegistrationForm, questionnaire: Questionnaire, confirmation: ConfirmationScreen, result_view: ResultView, box_renderer: BoxRenderer, table_renderer: TableRenderer, date_validator: DateValidator
    ) -> None:
        self.__console = console
        self.__form = form
        self.__questionnaire = questionnaire
        self.__confirmation = confirmation
        self.__result_view = result_view
        self.__box_renderer = box_renderer
        self.__table_renderer = table_renderer
        self.__date_validator = date_validator

    # ------------------------------------------------------------------
    # MENU AND FREE-TEXT INPUT
    # ------------------------------------------------------------------
    def ask_or_quit(self, prompt: str) -> str | None:
        """
        Ask a question and return the raw input,
        or None if the user typed quit.
        """
        text = self.__console.ask(prompt)
        if self.__is_quit(text):
            return None
        return text

    def choose(self, options: Sequence[Labelled], header: str | None = None, quittable: bool = False) -> Labelled | None:
        """
        Show a numbered menu and return the chosen option, or None if the input was not a valid option.
        A quittable menu also shows the quit hint and returns None if the user typed quit.
        """
        numbered = NumberedOptions(options)
        lines = numbered.lines()
        if quittable:
            lines.append(constants.QUIT_MENU_HINT)
        choice = self.__prompt_menu(lines, header)
        if quittable and self.__is_quit(choice):
            return None
        error = self.__validate_option(choice, len(numbered))
        if error is not None:
            self.show_message(error)
            return None
        return numbered.get(choice)

    def ask_date(self, prompt: str) -> str | None:
        """
        Ask for a YYYY-MM-DD date and return it, or return None if the
        user typed quit or the date is not valid (the error is shown).
        """
        date = self.__console.ask(prompt).strip()
        if self.__is_quit(date):
            return None
        error = self.__date_validator.validate(date)
        if error is not None:
            self.show_message(error)
            return None
        return date

    def __is_quit(self, text: str) -> bool:
        """
        Return True and show the quit message if the user typed quit,
        the same command the patient types to leave registration.
        """
        if text.strip().upper() != Navigation.QUIT.value:
            return False
        self.show_message(constants.QUIT_TO_MAIN_MENU_MESSAGE)
        return True

    def __prompt_menu(self, options: list[str], header: str | None = None) -> str:
        # Print the boxed menu, and return the normalised input.
        menu = self.__box_renderer.render(options, header)
        self.__console.show(menu)
        return self.__console.ask_normalised(constants.MENU_OPTION_PROMPT)

    def __validate_option(self, text: str, maximum: int) -> str | None:
        # Uses the menuoptionvalidator to validate the menu option.
        # maximum is the menu's number of options.
        # Guards against empty, non-integer, zero, negative and out of range inputs.
        return MenuOptionValidator(maximum=maximum).validate(text)

    # ------------------------------------------------------------------
    # REGISTRATION 
    # ------------------------------------------------------------------
    def collect_registration(self) -> dict[str, Answer] | None:
        """
        Run the questionnaire and the confirmation screen. 
        Returns the confirmed answers, or None if registration did not finish.
        """
        patient_answers = self.__questionnaire.run()
        if patient_answers is None:
            return None
        confirmed = self.__confirm(patient_answers)
        if confirmed is not None:
            self.show_message(constants.CONFIRMED_MESSAGE)
        # If program gets to this step, it means None is returned
        return confirmed

    def filter_for_ai(self, answers: Mapping[str, Answer]) -> dict[str, Answer]:
        # Returns only the values to be fed to the AI.
        return self.__form.filter_for_ai(answers)

    def __confirm(self, patient_answers: PatientAnswers) -> dict[str, Answer] | None:
        """
        Run the confirmation screen on the patient's answers and return the
        confirmed answers as a dict, or None if it did not finish.
        """
        # Runs the confirmation screen for patient's answers.
        # Returns the confirmed answer as a dict, 
        # unless the confirmation was interrupted or halted, in which it will return None.
        if not self.__confirmation.run(patient_answers):
            return None
        return patient_answers.to_dict()
    
    # ------------------------------------------------------------------
    # OUTPUT
    # ------------------------------------------------------------------
    def show_message(self, message: str) -> None:
        self.__console.show(message)

    def show_result(
        self, logic_result: Mapping[str, str | None]
    ) -> None:
        # Show the patient the result of their registration.
        # Such as their queue number and furhter instructions
        lines = self.__result_view.build_lines(logic_result)
        box = self.__box_renderer.render(lines, constants.RESULT_HEADER)
        self.__console.show(box)

    def show_table(
        self, report: pd.DataFrame | Mapping[str, object], title: str = ""
    ) -> None:
        # Shows a report or query in the form of a table.
        table = self.__table_renderer.render(report, title)
        self.__console.show(table)

    def table_fits_screen(self, columns: list[str]) -> bool:
    # Whether a table with these columns fits on screen or is too
    # wide and should be exported to a CSV instead.
        screen_width = self.__console.width()
        return self.__table_renderer.fits(columns, screen_width)
