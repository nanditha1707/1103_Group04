from collections.abc import Sequence

from app import constants
from app.numbered_options import NumberedOptions
from io_manager import IOManager

from .menu_action import MenuAction


class MainMenu:

    def __init__(
        self, io: IOManager, actions: Sequence[MenuAction]
    ) -> None:
        self.__io = io
        self.__actions = NumberedOptions(actions)

    def run_once(self) -> bool:
        choice = self.__io.prompt_menu(self.__actions.lines(), constants.MAIN_MENU_HEADER)
        action = self.__actions.find(choice)
        if action is None:
            self.__io.show_message(constants.INVALID_MENU_OPTION_MESSAGE)
            return True
        return action.run()
