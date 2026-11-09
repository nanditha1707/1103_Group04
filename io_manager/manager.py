from collections.abc import Iterable, Mapping

import pandas as pd

from io_manager import messages
from io_manager.console.console import Console
from io_manager.console.terminal_console import TerminalConsole
from io_manager.form.registration_factory import RegistrationFactory
from io_manager.patient_answers import Answer, PatientAnswers
from io_manager.rendering.box_renderer import BoxRenderer
from io_manager.rendering.table_renderer import TableRenderer
from io_manager.screens.confirmation_screen import ConfirmationScreen
from io_manager.screens.questionnaire import Questionnaire
from io_manager.screens.result_view import ResultView
from io_manager.symptoms.symptom_catalogue import SymptomCatalogue
from io_manager.validators.chain_validator import ChainValidator
from io_manager.validators.date_validator import DateValidator
from io_manager.validators.non_negative_integer_validator import NonNegativeIntegerValidator
from io_manager.validators.not_empty_validator import NotEmptyValidator


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
        self,
        console: Console | None = None,
        *,
        symptom_terms: Iterable[str],
        factory: RegistrationFactory | None = None,
    ) -> None:
        # Sets the default console to TerminalConsole, unless a separate console is fed to it during init.
        # Currently doesnt occur, will only come into play if other custom GUI's are created.
        self.__console = console if console is not None else TerminalConsole()

        # Sets the default factory/ registration setup to the RegistrationFactory class.
        if factory is None:
            factory = RegistrationFactory()

        self.__box_renderer = BoxRenderer()
        self.__table_renderer = TableRenderer()
        self.__option_validator = ChainValidator(
            [
                NotEmptyValidator(),
                NonNegativeIntegerValidator(
                    minimum=1, error=messages.POSITIVE_WHOLE_NUMBER_ERROR
                ),
            ]
        )
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
            self.__box_renderer,
            self.__option_validator,
        )
        self.__result_view = ResultView()

    # ------------------------------------------------------------------
    # MENU AND FREE-TEXT INPUT
    # ------------------------------------------------------------------
    def prompt_menu(self, options: list[str], header: str | None = None) -> str:
        # Print the boxed menu, and return the normalised input.
        self.__console.show(self.__box_renderer.render(options, header))
        return self.__console.ask(messages.MENU_OPTION_PROMPT).strip().upper()

    def ask(self, prompt: str) -> str:
        # Ask a questiion and return raw input.
        return self.__console.ask(prompt)

    def validate_option(self, text: str) -> str | None:
        # Uses a chainvalidator to validate the menu option
        # Guards against empty and negative integer input.
        return self.__option_validator.validate(text)

    def validate_date(self, text: str) -> str | None:
        # Checks if a DD-MM-YYYY date is valid.
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
            self.show_message(messages.CONFIRMED_MESSAGE)
        # If program gets to this step, it means None is returned
        return confirmed

    def filter_for_ai(self, answers: Mapping[str, Answer]) -> dict[str, Answer]:
        # Returns only the values to be fed to the AI.
        return self.__form.filter_for_ai(answers)

    def __confirm(self, patient_answers: PatientAnswers) -> dict[str, Answer] | None:
        """Run the confirmation screen on the patient's answers and return the
        confirmed answers as a dict, or None if it did not finish."""
        # Runs the confirmation screen for patient's answers.
        # Returns the confirmed answer as a dict, 
        # unless the confirmation was interrupted or halted, in which it will return None.
        if not self.__confirmation.run(patient_answers):
            return None
        return patient_answers.to_dict()
