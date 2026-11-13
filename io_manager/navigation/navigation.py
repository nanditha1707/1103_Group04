from enum import Enum

class Navigation(Enum):
    """
    Class that defines the possible outcomes,
    of a users input, when answering a question in the registration process.

    BACK and QUIT hold the exact text the patient types for those
    commands, which QuestionResult.from_input relies on to recognise them.
    """

    ANSWERED = "ANSWERED"
    INVALID = "INVALID"
    BACK = "BACK"
    QUIT = "QUIT"