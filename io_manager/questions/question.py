from abc import ABC, abstractmethod

from io_manager.console import Console
from io_manager.navigation import QuestionResult
from io_manager.patient_answers import PatientAnswers
from io_manager.rules import SkipRule
from typedefs import Answer


class Question(ABC):
    """
    One patient registration question.

    Holds the shared behaviour. Subclasses only decide how the answer is
    collected and how it is shown on the confirmation screen.
    """

    def __init__(
        self, key: str, prompt: str, share_with_ai: bool = False, skip_rule: SkipRule | None = None
    ) -> None:
        self.__key = key
        self.__prompt = prompt
        self.__share_with_ai = share_with_ai
        self.__skip_rule = skip_rule

    @property
    def key(self) -> str:
        """
        The key for the question, e.g. "nric", "name".
        """
        return self.__key

    @property
    def prompt(self) -> str:
        """
        The prompt to ask the user for the question, e.g. "Enter your Name: ".
        """
        return self.__prompt

    @property
    def share_with_ai(self) -> bool:
        """
        Return True if the user answer to this question is to be sent
        to the AI. Questions with personal details such as name and nric
        will return a False value so they are never fed into the AI.
        """
        return self.__share_with_ai

    def should_skip(self, answers: PatientAnswers) -> bool:
        """
        Return True if this question does not apply to the patient
        based on the user answers given so far.

        A question without a skip rule is never skipped. Otherwise the
        skip rule checks the earlier answers, e.g. the pregnancy question
        is skipped if the patient answered "M" for gender.
        """
        if self.__skip_rule is None:
            return False
        return self.__skip_rule.should_skip(answers)

    @abstractmethod
    def ask(self, console: Console, previous: Answer) -> QuestionResult:
        """
        Ask the question through the console and return a
        QuestionResult saying what the user did.

        previous is the answer the user gave earlier, or None if the
        question has not been answered yet. It lets a question continue
        from the earlier answer when the user comes back to it, e.g. the
        symptom menu starts with the symptoms already chosen.

        The result is ANSWERED with the validated value, INVALID with an
        error message, or BACK/QUIT if the user typed that command.
        Invalid input is returned as an INVALID result instead of being
        raised as an exception, so the caller can show the error and ask
        again.
        """

    @abstractmethod
    def display_value(self, value: Answer) -> str:
        """
        Return the user answer as text for the confirmation screen.

        Each subclass formats its own type of answer, e.g. a list of
        symptoms can be joined into one line. This lets the confirmation
        screen show every answer the same way without checking its type.
        """