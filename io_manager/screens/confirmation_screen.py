from io_manager import messages
from io_manager.console.console import Console
from io_manager.form.registration_form import RegistrationForm
from io_manager.navigation.navigation import Navigation
from io_manager.navigation.question_result import QuestionResult
from io_manager.patient_answers import PatientAnswers
from io_manager.rendering.box_renderer import BoxRenderer
from io_manager.rules.stop_rule import StopRule
from io_manager.validators.validator import Validator


class ConfirmationScreen:
    """Shows every answer so the patient can edit any of them before
    confirming.

    It only coordinates all the actions. The code that actually does the
    actions are in separate classes. BoxRenderer draws the menu, Validator
    checks the user answer, Question re-asks itself and StopRule decides
    whether registration ends.
    """

    def __init__(
        self, console: Console, form: RegistrationForm, stop_rule: StopRule, renderer: BoxRenderer, option_validator: Validator
        ) -> None:
        self.__console = console
        self.__form = form
        self.__stop_rule = stop_rule
        self.__renderer = renderer
        self.__option_validator = option_validator

    def run(self, answers: PatientAnswers) -> bool:
        """Return True once the answers are confirmed, or False if the
        patient quit or a stop rule ended registration (e.g. consent
        changed to N). Edits are made to answers in place."""
        questions = self.__form.questions

        while True:
            lines, editable = self.__menu_lines(answers)
            self.__console.show(
                self.__renderer.render(lines, messages.CONFIRMATION_HEADER)
            )
            choice = self.__console.ask(messages.MENU_OPTION_PROMPT).strip().upper()

            # back and quit are checked before the number check, so they
            # get their own response instead of the number error.
            command = QuestionResult.from_command(choice)
            if command is not None:
                if command.navigation is Navigation.QUIT:
                    self.__console.show(messages.REG_EXIT_MESSAGE)
                    return False
                # The only other command is BACK.
                self.__console.show(messages.CANNOT_GO_BACK)
                continue

            error = self.__option_validator.validate(choice)
            if error is not None:
                self.__console.show(error)
                continue

            option = int(choice)
            if option == self.__confirm_option:
                if self.__is_complete(answers):
                    return True
                continue

            # Menu numbers are question positions plus one.
            index = option - 1
            if index >= len(questions):
                self.__console.show(messages.INVALID_MENU_OPTION)
                continue
            if index not in editable:
                self.__console.show(messages.CANNOT_EDIT)
                continue

            if self.__edit(questions[index], answers) is Navigation.QUIT:
                self.__console.show(messages.REG_EXIT_MESSAGE)
                return False

            stop_message = self.__stop_rule.stop_message(answers)
            if stop_message:
                self.__console.show(stop_message)
                return False