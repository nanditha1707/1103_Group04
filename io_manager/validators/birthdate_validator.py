from datetime import date, datetime, tzinfo
from typing import override

from io_manager import constants

from .date_validator import DateValidator
from .validator import Validator


class BirthdateValidator(Validator):
    """
    Checks a birthdate is a real YYYY-MM-DD date that is no earlier than
    the earliest allowed birthdate and not in the future.

    The format and calendar checks are delegated to a DateValidator it
    holds (composition) so this class only adds the range check on top.
    It does not inherit from DateValidator because a birthdate check is
    stricter than a date check. A DateValidator accepts any real date
    including future ones, so a BirthdateValidator cannot stand in for it.
    """

    def __init__(
        self, earliest: date, timezone: tzinfo
    ) -> None:
        self.__date_validator = DateValidator(constants.BIRTHDATE_FORMAT_ERROR)
        self.__earliest = earliest
        self.__timezone = timezone

    @override
    def validate(self, answer: str) -> str | None:
        format_error = self.__date_validator.validate(answer)
        if format_error is not None:
            return format_error

        birthdate = date.fromisoformat(answer)
        today = datetime.now(self.__timezone).date()

        if not self.__earliest <= birthdate <= today:
            return constants.BIRTHDATE_RANGE_ERROR.format(
                earliest=self.__earliest.isoformat()
            )

        return None
