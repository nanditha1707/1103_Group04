from typing import override

from app import constants
from app.interfaces import UserPrompt

from .menu_action import MenuAction
from .password_gate import PasswordGate


class ExitAction(MenuAction):

    def __init__(
        self, prompt: UserPrompt, gate: PasswordGate
    ) -> None:
        super().__init__(constants.EXIT_LABEL)
        self.__prompt = prompt
        self.__gate = gate

    @override
    def run(self) -> bool:
        if not self.__gate.unlock(constants.EXIT_CODE_PROMPT):
            return True
        self.__prompt.show_message(constants.MENU_EXIT_MESSAGE)
        return False
