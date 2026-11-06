from enum import Enum

class Navigation(Enum):
    """Class that defines the possible outcomes,
    of a users input, when answering a question in the registration process.
    """

    ANSWERED = "ANSWERED"
    INVALID = "INVALID"
    BACK = "BACK"
    QUIT = "QUIT"

    @classmethod
    def from_command(cls, text: str) -> Navigation | None:
        """Return BACK or QUIT if the text is one of those commands,
        otherwise None."""
        if text == cls.BACK.value:
            return cls.BACK
        if text == cls.QUIT.value:
            return cls.QUIT
        return None