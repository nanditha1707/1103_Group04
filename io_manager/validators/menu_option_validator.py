from typing import override

from io_manager import constants

from .chain_validator import ChainValidator
from .non_negative_integer_validator import NonNegativeIntegerValidator
from .not_empty_validator import NotEmptyValidator
from .validator import Validator


class MenuOptionValidator(Validator):
    """
    Validator meant for checking menu option inputs.
    It first checks if the input is blank, then if it is a whole number
    from 1 (menus always start at 1) to the maximum.

    The two checks are run by a ChainValidator it holds (composition)
    instead of inheriting from ChainValidator, so how the checks are
    combined stays hidden inside this class.

    Every menu has a fixed number of options, so maximum is required and
    is the number of the last option. The default error covers both a
    non-number and a number past the last option, and shows the range,
    e.g. "from 1 to 4". A menu can pass its own messages instead.
    """

    def __init__(
        self, *, maximum: int, blank_error: str = constants.EMPTY_INPUT_ERROR, error: str | None = None
    ) -> None:
        # The default error needs the maximum filled in, which is only
        # known here. An error passed in by a menu is used as it is.
        if error is None:
            error = constants.INVALID_MENU_OPTION.format(maximum=maximum)
        self.__chain = ChainValidator([
            NotEmptyValidator(blank_error),
            NonNegativeIntegerValidator(minimum=1, maximum=maximum, error=error),
        ])

    @override
    def validate(self, answer: str) -> str | None:
        return self.__chain.validate(answer)
