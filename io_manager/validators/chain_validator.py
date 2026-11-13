from collections.abc import Sequence
from typing import override

from .validator import Validator


class ChainValidator(Validator):
    """
    Runs several validators in order and returns the first error.
    """

    # Sequence means validators must be an ordered collection such as a
    # list or tuple, because they run in the order given. 
    def __init__(
        self, validators: Sequence[Validator]
    ) -> None:
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