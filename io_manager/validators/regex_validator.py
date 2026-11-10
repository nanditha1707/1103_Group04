import re
from typing import override

from io_manager.validators.validator import Validator


class RegexValidator(Validator):
    """
    Accepts answers where the whole text matches a regex pattern.

    It is used for:
    1. Name
    2. NRIC
    3. Date

    All of these validations have different patterns:

        1. Name starts with a letter, followed by any letters, apostrophes,
        spaces or hyphens.
        2. NRIC starts with S, T, F, G or M, followed by 7 digits and a
        final letter e.g. S1234567D.
        3. Date is in YYYY-MM-DD format e.g. 2026-10-13.

        Since all of these only need the text to match a pattern, we used a
        common class that takes the pattern and error message as arguments.
        Name and NRIC each create their own instance, while date uses
        DateValidator subclass to add the calendar check. 
        
        Subclass is needed for date because in addition to checking whether
        the format matches for date, it needs to check whether the date 
        actually exists in the calendar.
    """

    def __init__(
        self, pattern: str, error: str
    ) -> None:
        self.__pattern = re.compile(pattern)
        # Protected, not private: subclasses such as DateValidator return
        # the same error for checks they add on top of the pattern.
        self._error = error

    @override
    def validate(self, answer: str) -> str | None:
        # fullmatch checks the entire text
        if self.__pattern.fullmatch(answer):
            return None
        return self._error
