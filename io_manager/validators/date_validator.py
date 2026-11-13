from datetime import datetime
from typing import override

from io_manager import constants

from .regex_validator import RegexValidator
from .validator import Validator


class DateValidator(Validator):
    """
    Checks a date is in YYYY-MM-DD format and exists on the calendar.
    Valid format but non-existent dates like 2026-02-30 are rejected.

    The format check is delegated to a RegexValidator it holds
    (composition) so this class only adds the calendar check on top.
    It does not inherit from RegexValidator so neither class needs to
    know the other's internals. Each keeps its own private copy of the
    error message.

    The error message can be passed in so classes that hold a
    DateValidator, such as BirthdateValidator, can reuse these checks
    with their own message.
    """

    PATTERN = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(
        self, error: str = constants.DATE_ERROR
    ) -> None:
        self.__format_validator = RegexValidator(self.PATTERN, error)
        self.__error = error

    @override
    def validate(self, answer: str) -> str | None:
        format_error = self.__format_validator.validate(answer)
        if format_error is not None:
            return format_error

        # strptime raises ValueError for dates that do not exist.
        try:
            datetime.strptime(answer, self.DATE_FORMAT)
        except ValueError:
            return self.__error

        # No error for valid dates
        return None
