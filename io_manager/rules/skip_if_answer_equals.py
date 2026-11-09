from typing import override

from io_manager.patient_answers import PatientAnswers
from io_manager.rules.skip_rule import SkipRule


class SkipIfAnswerEquals(SkipRule):
    """
    Skips a question when the value of an answer matches a given value. 
    An example of this is skipping the pregnancy question,
    if the patient has answered "M" for the gender question.
    """

    def __init__(self, key: str, value: Answer) -> None:
        self.__key = key
        self.__value = value

    @override
    def should_skip(self, answers: PatientAnswers) -> bool:
        return answers.get_answer(self.__key) == self.__value