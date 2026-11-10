from io_manager import messages
from io_manager.console.console import Console
from io_manager.form.registration_form import RegistrationForm
from io_manager.navigation.navigation import Navigation
from io_manager.patient_answers import PatientAnswers
from io_manager.rules.stop_rule import StopRule


class Questionnaire:
    """
    Takes the patient through the registration form once, from the
    first question to the last.

    It only coordinates all the actions. The code that actually does the
    actions is in separate classes. Question asks itself and checks the
    user answer, RegistrationForm saves each answer into PatientAnswers
    and decides which question comes next or before, and StopRule decides
    whether registration ends.

    Every question is asked through question.ask(), so this loop never
    checks what kind of question it has (TextQuestion or SymptomQuestion).

    Only the method run() is public since it is used by IOManager class.
    The other method is private since it is used within run() itself
    and does not need to be accessed from the outside.
    """

    def __init__(
        self, console: Console, form: RegistrationForm, stop_rule: StopRule
    ) -> None:
        self.__console = console
        self.__form = form
        self.__stop_rule = stop_rule

    def run(self) -> PatientAnswers | None:
        """
        Return the completed answers, or None if the patient quit or
        a stop rule ended registration (e.g. consent answered N). The
        message explaining why is shown here.
        """
        # A new PatientAnswers is created for each patient and handed
        # back to the caller.
        answers = PatientAnswers()
        questions = self.__form.questions

        # index is the position of the question being asked, starting
        # from the first question (consent).
        index = 0

        # Keep asking until index moves past the last question. index
        # does not always go up by one: BACK moves it backwards, an
        # invalid answer keeps it the same and skipped questions are
        # passed over.
        while index < len(questions):
            question = questions[index]

            # Ask the current question. The previous answer is passed in
            # so a question can start from it when the patient goes back
            # (e.g. the symptom list keeps the symptoms already added).
            result = question.ask(self.__console, answers.get_answer(question.key))

            # First checks if the user typed QUIT. Stop registration
            # straight away and show the exit message.
            if result.navigation is Navigation.QUIT:
                self.__console.show(messages.REG_EXIT_MESSAGE)
                return None

            # Secondly checks if the user typed BACK. Unlike the
            # confirmation screen, going back is allowed here since the
            # patient may want to change the answer they just gave.
            if result.navigation is Navigation.BACK:
                index = self.__go_back(index, answers)
                continue

            # If the answer failed validation then show the error message
            # and re-ask the same question.
            if result.navigation is Navigation.INVALID:
                self.__console.show(result.error)
                continue

            # If no error then the answer is valid, so store it. The form
            # also clears any question that no longer applies,
            # e.g. answering gender M makes pregnancy not applicable.
            self.__form.apply_answer(answers, question.key, result.value)

            # Move on to the next question that applies, passing over
            # skipped ones (e.g. gender M jumps over pregnancy).
            index = self.__form.next_index(index, answers)

            # Check the stop rule after every answer. Consent N, an
            # emergency answer or being under age ends registration
            # straight away. The same StopRule is used by the
            # confirmation screen, so both stop for the same reasons.
            stop_message = self.__stop_rule.stop_message(answers)
            if stop_message:
                self.__console.show(stop_message)
                return None

        # The loop only ends once every question that applies has been
        # answered, so the answers are complete.
        return answers

    def __go_back(self, index: int, answers: PatientAnswers) -> int:
        """
        Return the index of the question to ask after the patient
        types BACK. Used when user types BACK on any question.

        Example: if the RegistrationForm only had four questions
        (consent, gender, pregnancy and chest pain), and the patient
        answered M for gender. For the current index below, when the
        patient types BACK from:

            3 (chest pain)  returns 1 (gender), passing over pregnancy
                            because it is skipped for M

            1 (gender)      returns 0 (consent)

            0 (consent)     shows "There is no further step to go back
                            to. If you would like to exit, type 'quit'."
                            and returns 0, so consent is asked again
        """
        # The first question has nothing before it, so show the message
        # and stay on the same question.
        if index == 0:
            self.__console.show(messages.NO_PREVIOUS_QUESTION)
            return index

        # RegistrationForm finds the previous question that applies.
        return self.__form.previous_index(index, answers)
