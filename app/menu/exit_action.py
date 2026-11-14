from typing import override

from app import constants
from app.interfaces import UserPrompt

from .menu_action import MenuAction


class ExitAction(MenuAction):

    def __init__(
        self, prompt: UserPrompt
    ) -> None:
        super().__init__(constants.EXIT_LABEL)
        self.__prompt = prompt

    @override
    def run(self) -> bool:
        inputted_pass = self.__prompt.ask(constants.EXIT_CODE_PROMPT)
        if inputted_pass == constants.ADMIN_PASSWORD:
            self.__prompt.show_message(constants.MENU_EXIT_MESSAGE)
            return False
        self.__prompt.show_message(constants.WRONG_PASSWORD_MESSAGE)
        return True
