import hmac

from app import constants
from app.interfaces import UserPrompt


class PasswordGate:
    """
    Asks for the admin password and says whether it was right.
    Exit and the healthcare portal share one gate so they always check the same password.
    """

    def __init__(
        self, prompt: UserPrompt, password: str
    ) -> None:
        self.__prompt = prompt
        self.__password = password

    def unlock(self, question: str) -> bool:
        answer = self.__prompt.ask(question)
        if hmac.compare_digest(answer.encode(), self.__password.encode()):
            return True
        self.__prompt.show_message(constants.WRONG_PASSWORD_MESSAGE)
        return False
