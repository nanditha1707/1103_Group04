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
        error = self.__io.validate_option(choice, len(self.__actions))
        if error is not None:
            self.__io.show_message(error)
            return True
        return self.__actions.get(choice).run()
