from typing import override

from .validator import Validator


class NonNegativeIntegerValidator(Validator):
    """
    Validates user inputs for integers >=0 between a minimum and an 
    optional maximum (both inclusive). We use it mainly for 3 different
    validations:

    1. Validate age
    2. Validate menu options
    3. Validate symptom onset days (days since symptom started)
    
    All of these validations have different acceptable ranges:

    1. Age between 0 (infants can be 0 years old) and 150
    2. Menu options between 1 (menus start at 1) and the menu's number
    of options. This is done through MenuOptionValidator.
    3. 0 (symptoms started today) and 365

    Since these are all non negative integers, we used one common class
    for all of them. Age and symptom onset days each create their own
    instance with their own range, and MenuOptionValidator creates one
    for each menu.
    """

    def __init__(
        self, *, minimum: int, error: str, maximum: int | None = None
    ) -> None:
        self.__minimum = minimum
        self.__maximum = maximum
        self.__error = error

    @override
    def validate(self, answer: str) -> str | None:

        # Accept only text made entirely of digits, i.e. a non-negative
        # integer with no sign, spaces or decimal point.
        if not answer.isdecimal():
            return self.__error

        # This is to handle very long strings that pass .isdecimal() check.
        # Python refuses to convert extremely long digit strings, so
        # that is handled and treated as invalid instead of crashing.
        try:
            value = int(answer)
        except ValueError:
            return self.__error

        if value < self.__minimum:
            return self.__error

        # maximum is optional, so it is only checked when one is given.
        if self.__maximum is not None and value > self.__maximum:
            return self.__error

        # No errors
        return None
