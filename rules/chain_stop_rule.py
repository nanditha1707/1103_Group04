from collections.abc import Sequence
from typing import override

from io_manager.answer_sheet import AnswerSheet
from io_manager.rules.stop_rule import StopRule


class ChainStopRule(StopRule):
    """
    Runs several stop rules in order and returns the earliest matched error message.
    """

    def __init__(self, rules: Sequence[StopRule]) -> None:
        self.__rules = tuple(rules)

    @override
    def stop_message(self, answers: AnswerSheet) -> str | None:
        for rule in self.__rules:
            message = rule.stop_message(answers)
            if message:
                return message
        return None
