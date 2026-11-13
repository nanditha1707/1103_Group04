from typing import override

from app import constants
from io_manager import IOManager

from .menu_action import MenuAction


class ExitAction(MenuAction):

    def __init__(
        self, io: IOManager
    ) -> None:
        super().__init__(constants.EXIT_LABEL)
        self.__io = io

    @override
    def run(self) -> bool:
        inputted_pass = self.__io.ask(constants.EXIT_CODE_PROMPT)
        if inputted_pass == constants.ADMIN_PASSWORD:
            self.__io.show_message(constants.MENU_EXIT_MESSAGE)
            return False
        self.__io.show_message(constants.WRONG_PASSWORD_MESSAGE)
        return True
