from typing import override

from io_manager import messages
from io_manager.console.console import Console
from io_manager.navigation.question_result import QuestionResult
from io_manager.patient_answers import Answer
from io_manager.questions.question import Question
from io_manager.rules.skip_rule import SkipRule
from io_manager.validators.validator import Validator


class TextQuestion(Question):
    """A question answered by typing one line, checked by a Validator
    passed in from outside (aggregation)."""

    def __init__(
        self, key: str, prompt: str, validator: Validator, share_with_ai: bool = False, skip_rule: SkipRule | None = None
        ) -> None:
        super().__init__(key, prompt, share_with_ai, skip_rule)
        self.__validator = validator

    @override
    def ask(self, console: Console, previous: Answer) -> QuestionResult:
        raw = console.ask_normalised(self.prompt)

        command = QuestionResult.from_command(raw)
        if command is not None:
            return command

        if not raw:
            return QuestionResult.invalid(messages.EMPTY_INPUT_ERROR)

        error = self.__validator.validate(raw)
        if error is not None:
            return QuestionResult.invalid(error)
        return QuestionResult.answered(raw)

    @override
    def display_value(self, value: Answer) -> str:
        if value is None:
            return messages.NOT_ANSWERED
        # A typed answer is always text.
        return value
