from typing import override

from io_manager import constants
from io_manager.patient_answers import PatientAnswers

from .stop_rule import StopRule


class MinimumAgeRule(StopRule):
    """
    Returns the underage message if the patient is too young to self register.
    It is done this way to ensure the logic is preserved between Questionnaire and Confirmation screens.

    The underage message will be used in Questionnaire and Confirmation
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
        # Age is worked out from the birthdate by AgeFromBirthdate
        # so None means the birthdate question has not been answered yet.
        if age is None:
            return None
        # If the age question has been answered and ,
        # the patient's age is less than the minimum, 
        # return the underage message with the minimum age filled in.
        if int(age) < self.__minimum:
            return constants.UNDERAGE_MESSAGE.format(minimum=self.__minimum)
        return None
