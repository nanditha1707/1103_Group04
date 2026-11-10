from typing import override

from io_manager import constants

from .validator import Validator


class NotEmptyValidator(Validator):
    """
    Rejects blank answers.
    """

    def __init__(
        self, error: str = constants.EMPTY_INPUT_ERROR
    ) -> None:
        self.__error = error

    @override
    def validate(self, answer: str) -> str | None:
        # if user answer (is not empty), return None
        if answer:
            return None
        # return error when it is empty
        return self.__error