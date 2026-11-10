from io_manager import messages
from io_manager.console.console import Console
from io_manager.form.registration_form import RegistrationForm
from io_manager.navigation.navigation import Navigation
from io_manager.navigation.question_result import QuestionResult
from io_manager.patient_answers import PatientAnswers
from io_manager.questions.question import Question
from io_manager.rendering.box_renderer import BoxRenderer
from io_manager.rules.stop_rule import StopRule
from io_manager.validators.menu_option_validator import MenuOptionValidator


class ConfirmationScreen:
    """Shows every answer so the patient can edit any of them before
    confirming.

    It only coordinates all the actions. The code that actually does the
    actions are in separate classes. BoxRenderer draws the menu,
    MenuOptionValidator checks the menu option, Question re-asks itself and StopRule decides
    whether registration ends.

    Only the method run() is public since it is used by IOManager class.
    The other methods are private since they are used within run() itself
    and does not need to be accessed from the outside.
    """

    def __init__(
        self, console: Console, form: RegistrationForm, stop_rule: StopRule, renderer: BoxRenderer
        ) -> None:
        self.__console = console
        self.__form = form
        self.__stop_rule = stop_rule
        self.__renderer = renderer
        self.__option_validator = MenuOptionValidator(
            # self.__confirm_option returns the value of the final option.
            maximum=self.__confirm_option,
        )

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
            choice = self.__console.ask_normalised(messages.MENU_OPTION_PROMPT)

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

            # Secondly validates the user choice. The validator returns an
            # error message string if the choice is blank or not a whole
            # number from 1 to the Confirm All Inputs option, and None if
            # there is no error. So after this, choice is always a valid
            # menu number.
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

            # If user choice is a question that cannot be edited.
            # This is if gender is 'M' and the user selects pregancy
            # question to edit. Prevent the user from editing by showing
            # cannot edit message and re-ask for input.
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

    @property
    def __confirm_option(self) -> int:
        """Confirm All Inputs is the menu line after the last question."""
        return len(self.__form.questions) + 1

    def __menu_lines(self, answers: PatientAnswers) -> tuple[list[str], set[int]]:
        """Build one line per question, so each menu number always
        matches the question's position, plus Confirm All Inputs. Also
        return the positions the patient may edit.

        Example: if the RegistrationForm only had three questions
        (gender, pregnancy and chest pain), and the patient answered M
        for gender and N for chest pain, this returns the tuple:

            (
                [
                    "01. Enter your Gender [M/F]: M",
                    "02. Are you currently pregnant? (Y/N): Not Applicable",
                    "03. Are you currently experiencing chest pain? (Y/N): N",
                    "04. Confirm All Inputs",
                    "You can also input quit",
                ],
                {0, 2},
            )

        The list is the menu lines. The set is the positions that can be
        edited.Pregnancy is not in the set because it is skipped for M.
        """
        lines: list[str] = []
        editable: set[int] = set()

        for index, question in enumerate(self.__form.questions):
            # Skipped questions do not apply, so they cannot be edited.
            if question.should_skip(answers):
                value = messages.NOT_APPLICABLE
            else:
                value = question.display_value(answers.get_answer(question.key))
                editable.add(index)
            lines.append(f"{index + 1:02d}. {question.prompt}{value}")

        lines.append(f"{self.__confirm_option:02d}. {messages.CONFIRM_ALL_LABEL}")
        lines.append(messages.CONFIRMATION_MENU_HINT)
        return lines, editable

    def __edit(self, question: Question, answers: PatientAnswers) -> Navigation:
        """Ask one question again and store the new answer if valid.
        Used when user chooses a valid question to edit. Returns the
        Navigation of the result so run() knows if the patient quit.

        Example: user selected the gender question to edit, and current 
        answers holds F for gender and N for pregnancy. For the new user
        answers below:

            M     answers becomes gender M, pregnancy None.
                  returns Navigation.ANSWERED

            X     shows "This is not a valid input, please only enter
                  either M or F."
                  answers unchanged, returns Navigation.INVALID

            BACK  shows the CANNOT_GO_BACK message
                  answers unchanged, returns Navigation.BACK

            QUIT  shows nothing here (run() shows the exit message)
                  answers unchanged, returns Navigation.QUIT
        """
        result = question.ask(self.__console, answers.get_answer(question.key))

        if result.navigation is Navigation.BACK:
            self.__console.show(messages.CANNOT_GO_BACK)

        elif result.navigation is Navigation.INVALID:
            self.__console.show(result.error)

        elif result.navigation is Navigation.ANSWERED:
            answers.record_answer(question.key, result.value)
            # e.g. gender changed to M makes pregnancy not applicable.
            self.__form.mark_skipped(answers)

        return result.navigation

    def __is_complete(self, answers: PatientAnswers) -> bool:
        """Return True if every question that applies has an answer. A
        question may have started to apply after an edit (gender M to
        F), so it must be answered first."""
        missing = self.__form.first_unanswered(answers)
        if missing is None:
            return True
        self.__console.show(
            messages.UNANSWERED_QUESTION.format(prompt=missing.prompt.strip())
        )
        return False