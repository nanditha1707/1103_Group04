from datetime import date, datetime, tzinfo
from typing import override

from io_manager import constants

from .date_validator import DateValidator


class BirthdateValidator(DateValidator):
    """
    Checks a birthdate is a real YYYY-MM-DD date that is no earlier than
    the earliest allowed birthdate and not in the future.

    The format and calendar checks are reused from DateValidator
    so this class only adds the range check on top.
    """

    def __init__(
        self, earliest: date, timezone: tzinfo
    ) -> None:
        super().__init__(constants.BIRTHDATE_FORMAT_ERROR)
        self.__earliest = earliest
        self.__timezone = timezone

    @override
    def validate(self, answer: str) -> str | None:
        format_error = super().validate(answer)
        if format_error is not None:
            return format_error

        birthdate = date.fromisoformat(answer)
        today = datetime.now(self.__timezone).date()

        if not self.__earliest <= birthdate <= today:
            return constants.BIRTHDATE_RANGE_ERROR.format(
                earliest=self.__earliest.isoformat()
            )

        return None
