from typing import override

from io_manager import constants
from io_manager.patient_answers import PatientAnswers

from .stop_rule import StopRule


class MinimumAgeRule(StopRule):
    """
    Returns the manual registration message if the patient is too young to self register. 
    It is done this way to ensure the logic is preserved between Questionnaire and Confirmation screens.

    The manual registration message will be used in Questionnaire and Confirmation, 
    to end the registration process if the patient is too young to self register.
    """

    def __init__(
        self, key: str, minimum: int
    ) -> None:
        self.__minimum = minimum
        self.__key = key

    @override
    def stop_message(self, answers: PatientAnswers) -> str | None:
        age = answers.get_answer(self.__key)
        # None means the age question has not been answered yet.
        if age is None:
            return None
        # If the age question has been answered and ,
        # the patient's age is less than the minimum, 
        # return the manual registration message.
        if int(age) < self.__minimum:
            return constants.MANUAL_REGISTRATION_MESSAGE
        return None
