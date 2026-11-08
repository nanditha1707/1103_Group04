from collections.abc import Sequence
from typing import override

from io_manager.validators.validator import Validator


class ChainValidator(Validator):
    """Runs several validators in order and returns the first error.

    Used for menu options, where the empty input check must run before 
    the non negative integer check so an empty input gets the correct 
    empty input error instead of the non negative integer error.
    """

    # Sequence means validators must be an ordered collection such as a
    # list or tuple, because they run in the order given. 
    def __init__(self, validators: Sequence[Validator]) -> None:
        self.__validators = tuple(validators)

    @override
    def validate(self, answer: str) -> str | None:
        for validator in self.__validators:
            # Runs validator
            error = validator.validate(answer)

            # Validator returns None only if validator has no error.
            # If not None then there is error, return the error message.
            if error is not None:
                return error
    
        # No error
        return None