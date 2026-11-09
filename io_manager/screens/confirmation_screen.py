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
            # shows the confirmation screen box
            lines, editable = self.__menu_lines(answers)

            # shows the confirmation screen box
            self.__console.show(
                self.__renderer.render(lines, messages.CONFIRMATION_HEADER)
            )
            # prompt user for choice: Enter either a number to edit the
            # respective question or enter 17 for done / confirm inputs
            choice = self.__console.ask(messages.MENU_OPTION_PROMPT).strip().upper()

            # First checks if the user choice is a command: QUIT or BACK
            command = QuestionResult.from_command(choice)
            if command is not None:
                if command.navigation is Navigation.QUIT:
                    self.__console.show(messages.REG_EXIT_MESSAGE)
                    return False
                # Prevent the user from going back and show message.
                # We dont want user to go back from confirmation screen
                # because no point: user can already edit all questions
                # from confirmation screen.
                self.__console.show(messages.CANNOT_GO_BACK)
                continue

            # Secondly validates the user choice and whether its a valid
            # integer. Validator returns error message string if error,
            # None if no error. This in practice rejects all inputs
            # that are not 
            error = self.__option_validator.validate(choice)

            # If error then print error message and re-ask user for input.
            if error is not None:
                self.__console.show(error)
                continue

            # If no error then see if user choice is to edit a question
            # or confirm all inputs.
            option = int(choice)

            # If user choice is to confirm all inputs.
            if option == self.__confirm_option:
                if self.__is_complete(answers):
                    return True
                continue

            # If user choice is to edit a question.
            # Menu numbers are question positions plus one, so question
            # index is question positions minus 1.
            index = option - 1

            # If user choice is integer more than the questions available
            # then show invalid menu option message and reprompt.
            # This is checked here instead of in the NonNegativeIntegerValidator
            # since the validator is shared by other menu screens with
            # a differing maximum number of menu options. 
            if index >= len(questions):
                self.__console.show(messages.INVALID_MENU_OPTION)
                continue

            # If user choice is a question that cannot be edited.
            # This is if gender is 'M' and the user selects pregancy
            # question to edit. Prevent the user from editing by showing
            # cannot edit message and re-ask for input
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