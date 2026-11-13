from io_manager.patient_answers import Answer
from io_manager.validators import Validator

from .navigation import Navigation


class QuestionResult:
    """
    The class that holds the result of every question asked and every menu input,
    and builds a result from the patient's input through from_input.
    The navigation attribute is an enum that says what happened, value holds the value of any valid input, and
    error holds the error message and is only used for invalid inputs. The attributes are private and only readable through properties, 
    so a result cannot be changed after it is created. 
    """

    def __init__(
        self, navigation: Navigation, value: Answer = None, error: str | None = None
    ) -> None:
        self.__navigation = navigation
        self.__value = value
        self.__error = error

    @property
    def navigation(self) -> Navigation:
        return self.__navigation

    @property
    def value(self) -> Answer:
        return self.__value

    @property
    def error(self) -> str | None:
        return self.__error

    @classmethod
    def answered(cls, value: str | list[str]) -> QuestionResult:
        # Stores the value for validated input,
        # and returns a QuestionResult with the navigation set to ANSWERED.
        return cls(Navigation.ANSWERED, value=value)

    @classmethod
    def invalid(cls, error: str) -> QuestionResult:
        # Return error message for input that fails validation,
        # and returns a QuestionResult with the navigation set to INVALID.
        return cls(Navigation.INVALID, error=error)

    @classmethod
    def back(cls) -> QuestionResult:
        return cls(Navigation.BACK)

    @classmethod
    def quit(cls) -> QuestionResult:
        return cls(Navigation.QUIT)

    @classmethod
    def from_input(cls, text: str, validator: Validator) -> QuestionResult:
        """
        Turn one line of normalised input into a result, in a fixed order:
        BACK or QUIT if it is a command, INVALID if the validator rejects it,
        otherwise ANSWERED with the text.
        Used by every screen that reads typed input, so they all treat
        commands and errors the same way, and the order lives only here.
        """
        command = cls.__from_command(text)
        if command is not None:
            return command
        error = validator.validate(text)
        if error is not None:
            return cls.invalid(error)
        return cls.answered(text)

    @classmethod
    def __from_command(cls, text: str) -> QuestionResult | None:
        """
        Return a BACK or QUIT result if the text is that specific command or input,
        otherwise None so from_input carries on validating the text.
        Private, so commands are only ever checked as part of from_input.
        """
        if text == Navigation.BACK.value:
            return cls.back()
        if text == Navigation.QUIT.value:
            return cls.quit()
        return None
