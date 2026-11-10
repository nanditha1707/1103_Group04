from typing import override

from io_manager import messages
from io_manager.patient_answers import PatientAnswers

from .stop_rule import StopRule


class ConsentRequiredRule(StopRule):
    """
    Returns the registration exit message if the patient does not consent. 
    It is done this way to ensure that the logic for changing consent to "N" will be reusable, 
    allowing the patient to withdraw consent and halt the registration process,
    at any point where consent is asked or confirmed.

    The exit message will be used in Questionnaire and Confirmation, 
    to end the registration process if the patient does not consent.

    """

    def __init__(
        self, key: str
    ) -> None:
        self.__key = key

    @override
    def stop_message(self, answers: PatientAnswers) -> str | None:
        if answers.get_answer(self.__key) == "N":
            return messages.REG_EXIT_MESSAGE
        return None