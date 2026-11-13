from collections.abc import Iterable, Mapping, Sequence

import pandas as pd

from io_manager import constants
from io_manager.console import Console, TerminalConsole
from io_manager.form import RegistrationFactory
from io_manager.menus import Labelled, NumberedOptions
from io_manager.patient_answers import Answer, PatientAnswers
from io_manager.rendering import BoxRenderer, TableRenderer
from io_manager.screens import ConfirmationScreen, Questionnaire, ResultView
from io_manager.symptoms import SymptomCatalogue
from io_manager.validators import DateValidator, MenuOptionValidator


class IOManager:
    """
    The orchestrator class main.py uses for all input and output.

    It builds the shared objects the other classes need,
    and passes them in through each constructor, so every part uses the same ones. 
    The console can be passed in, such as a GUI, otherwise,
    it defaults to a TerminalConsole, and the questions and stop rules come from a RegistrationFactory, 
    so a new front end or clinic setup needs no change to this class.
    """

    def __init__(
        self, console: Console | None = None, *, symptom_terms: Iterable[str], factory: RegistrationFactory | None = None
    ) -> None:
        # Sets the default console to TerminalConsole, unless a separate console is fed to it during init.
        # Currently doesnt occur, will only come into play if other custom GUI's are created.
        if console is not None:
            self.__console = console
        else:
            self.__console = TerminalConsole()

        # Sets the default factory/ registration setup to the RegistrationFactory class.
        if factory is None:
            factory = RegistrationFactory()

        self.__box_renderer = BoxRenderer()
        self.__table_renderer = TableRenderer()
        self.__date_validator = DateValidator()

        catalogue = SymptomCatalogue(symptom_terms)
        self.__form = factory.build_form(catalogue, self.__box_renderer)
        # Shared by both screens, so they always stop for the same reasons.
        stop_rule = factory.build_stop_rule()

        self.__questionnaire = Questionnaire(self.__console, self.__form, stop_rule)
        self.__confirmation = ConfirmationScreen(
            self.__console,
            self.__form,
            stop_rule,
            self.__box_renderer
        )
        self.__result_view = ResultView()

    # ------------------------------------------------------------------
    # MENU AND FREE-TEXT INPUT
    # ------------------------------------------------------------------
    def prompt_menu(self, options: list[str], header: str | None = None) -> str:
        # Print the boxed menu, and return the normalised input.
        menu = self.__box_renderer.render(options, header)
        self.__console.show(menu)
        return self.__console.ask_normalised(constants.MENU_OPTION_PROMPT)

    def ask(self, prompt: str) -> str:
        # Ask a questiion and return raw input.
        return self.__console.ask(prompt)

    def validate_option(self, text: str, maximum: int) -> str | None:
        # Uses the menuoptionvalidator to validate the menu option.
        # maximum is the menu's number of options, e.g. len(FILTER_OPTIONS).
        # Guards against empty, non-integer, zero, negative and out of range inputs.
        return MenuOptionValidator(maximum=maximum).validate(text)

    def choose[T: Labelled](self, options: Sequence[T], header: str | None = None) -> T | None:
        numbered = NumberedOptions(options)
        choice = self.prompt_menu(numbered.lines(), header)
        error = self.validate_option(choice, len(numbered))
        if error is not None:
            self.show_message(error)
            return None
        return numbered.get(choice)

    def validate_date(self, text: str) -> str | None:
        # Checks if a YYYY-MM-DD date is valid.
        return self.__date_validator.validate(text)

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
        self, ai_output: Mapping[str, object], logic_result: Mapping[str, str | None]
    ) -> None:
        # Show the patient the result of their registration. 
        # Such as their queue number and furhter instructions
        lines = self.__result_view.build_lines(ai_output, logic_result)
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
