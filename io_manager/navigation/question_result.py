from io_manager.answer_sheet import Answer
from io_manager.navigation.navigation import Navigation


class QuestionResult:
    """
    The class that holds the result of every question asked and every menu input.
    The navigation attribute is an enum that says what happened, value holds the value of any valid input, and
    error holds the error message and is only used for invalid inputs. The attributes are private and only readable through properties, 
    so a result cannot be changed after it is created. 
    """

    def __init__(
        self,
        navigation: Navigation,
        value: Answer = None,
        error: str | None = None,
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
    def from_command(cls, text: str) -> QuestionResult | None:
        """
        Return a BACK or QUIT result if the text is that specific command or input,
        otherwise None so the caller carries on validating the text.
        Acts as a way to intercept commands before they are validated as answers.
        """
        if text == Navigation.BACK.value:
            return cls.back()
        if text == Navigation.QUIT.value:
            return cls.quit()
        return None
