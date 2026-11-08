from collections.abc import Iterable
from typing import override

from io_manager import messages
from io_manager.answer_sheet import AnswerSheet
from io_manager.rules.stop_rule import StopRule


class EmergencyAnswerRule(StopRule):

    """
    Returns the nurse alert message if the patient answers Y to any emergency question, 
    so they see a nurse immediately. 
    It is done this way to ensure the logic is preserved between Questionnaire and Confirmation screens.

    The nurse alert message will be used in Questionnaire and Confirmation, 
    to end the registration process if the patient is in urgent need of medical attention.
    """

    # Uses iterable as order does not matter.
    def __init__(self, keys: Iterable[str]) -> None:
        self.__keys = tuple(keys)

    @override
    def stop_message(self, answers: AnswerSheet) -> str | None:
        for key in self.__keys:
            if answers.get_answer(key) == "Y":
                return messages.NURSE_ALERT_MESSAGE
        return None