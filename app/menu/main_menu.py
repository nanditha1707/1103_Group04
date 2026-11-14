from collections.abc import Sequence

from app import constants
from app.interfaces import UserPrompt

from .menu_action import MenuAction


class MainMenu:

    def __init__(
        self, prompt: UserPrompt, actions: Sequence[MenuAction]
    ) -> None:
        self.__prompt = prompt
        self.__actions = list(actions)

    def run_once(self) -> bool:
        action = self.__prompt.choose(self.__actions, constants.MAIN_MENU_HEADER)
        if action is None:
            return True
        return action.run()
