from abc import ABC, abstractmethod

from io_manager.answer_sheet import Answer, AnswerSheet
from io_manager.console.console import Console
from io_manager.navigation.question_result import QuestionResult
from io_manager.rules.skip_rule import SkipRule


class Question(ABC):
    """One patient registration question.

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
        """The key for the question, e.g. "nric", "name"."""
        return self.__key

    @property
    def prompt(self) -> str:
        """The prompt to ask the user for the question, e.g. "Enter your Name: "."""
        return self.__prompt

    @property
    def share_with_ai(self) -> bool:
        """Return True if the user answer to this question is to be sent
        to the AI. Questions with personal details such as name and nric
        will return a False value so they are never fed into the AI."""
        return self.__share_with_ai

    def should_skip(self, answers: AnswerSheet) -> bool:
        """Return True if this question does not apply to the patient
        based on the user answers given so far.
        """
        return self.__skip_rule is not None and self.__skip_rule.should_skip(answers)

    @abstractmethod
    def ask(self, console: Console, previous: Answer) -> QuestionResult:
        """
        """

    @abstractmethod
    def display_value(self, value: Answer) -> str:
        """Return the user answer as text for the confirmation screen."""