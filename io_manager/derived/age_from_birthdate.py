from datetime import date, datetime, tzinfo
from typing import override

from io_manager.patient_answers import Answer, PatientAnswers

from .derived_answer import DerivedAnswer


class AgeFromBirthdate(DerivedAnswer):
    """
    Works out the patient's age in whole years from their birthdate.

    The age is what gets sent to the AI and checked by MinimumAgeRule
    while the patient only ever sees their birthdate.
    """

    def __init__(
        self, key: str, birthdate_key: str, timezone: tzinfo, share_with_ai: bool = False
    ) -> None:
        super().__init__(key, share_with_ai)
        self.__birthdate_key = birthdate_key
        self.__timezone = timezone

    @override
    def compute(self, answers: PatientAnswers) -> Answer:
        birthdate_text = answers.get_answer(self.__birthdate_key)
        if birthdate_text is None:
            return None

        birthdate = date.fromisoformat(birthdate_text)
        today = datetime.now(self.__timezone).date()

        had_birthday = (today.month, today.day) >= (birthdate.month, birthdate.day)
        age = today.year - birthdate.year
        if not had_birthday:
            age -= 1

        return str(age)
