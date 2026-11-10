from io_manager.console.console import Console
from io_manager.validators.yes_no_validator import YesNoValidator


class YesNoPrompt:
    """Asks a Y/N follow-up question until the patient types Y or N.

    Used by the symptom actions, so an invalid answer such as "yes" is
    explained and asked again instead of being silently treated as No
    or dropping the patient back to the menu.
    """

    def __init__(self, validator: YesNoValidator) -> None:
        self.__validator = validator

    def confirm(self, console: Console, prompt: str) -> bool:
        while True:
            answer = console.ask_normalised(prompt)
            error = self.__validator.validate(answer)
            if error is None:
                # Compares answer to the YES constant in the YesNoValidator class,
                # and returns True if they match, otherwise returns False.
                return answer == YesNoValidator.YES
            # If there is an error, 
            # show the error message and ask the question again.
            console.show(error)
