from collections.abc import Iterable
from typing import override

from io_manager.validators.validator import Validator


class ChoiceValidator(Validator):
    """
    Accepts only user answers from a fixed set of choices, e.g. M or F.
    """

    # Iterable means choices can be anything that can be looped over,
    # such as a tuple, list or set. For example: ("M", "F").
    def __init__(
        self, choices: Iterable[str], error: str
    ) -> None:
        # Converted to tuple so allowed choices cannot be changed later.
        self.__choices = tuple(choices)
        self.__error = error

    @override
    def validate(self, answer: str) -> str | None:
        if answer in self.__choices:
            return None
        return self.__error