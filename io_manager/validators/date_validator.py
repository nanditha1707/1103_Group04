from datetime import datetime
from typing import override

from io_manager import constants

from .regex_validator import RegexValidator


class DateValidator(RegexValidator):
    """
    Checks a date is in YYYY-MM-DD format and exists on the calendar.
    Valid format but non-existent dates like 2026-02-30 are rejected.

    The error message can be passed in so subclasses such as
    BirthdateValidator can reuse these checks with their own message.
    """

    PATTERN = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
    DATE_FORMAT = "%Y-%m-%d"

    # super() calls RegexValidator __init__
    def __init__(
        self, error: str = constants.DATE_ERROR
    ) -> None:
        super().__init__(self.PATTERN, error)

    @override
    def validate(self, answer: str) -> str | None:
        format_error = super().validate(answer)
        if format_error is not None:
            return format_error

        # strptime raises ValueError for dates that do not exist.
        try:
            datetime.strptime(answer, self.DATE_FORMAT)
        except ValueError:
            return self._error

        # No error for valid dates
        return None
