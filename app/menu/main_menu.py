from collections.abc import Sequence

from app import constants
from io_manager import IOManager

from .menu_action import MenuAction


class MainMenu:

    def __init__(
        self, io: IOManager, actions: Sequence[MenuAction]
    ) -> None:
        self.__io = io
        self.__actions = list(actions)

    def run_once(self) -> bool:
        action = self.__io.choose(self.__actions, constants.MAIN_MENU_HEADER)
        if action is None:
            return True
        return action.run()
