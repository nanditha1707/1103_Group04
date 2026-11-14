from collections.abc import Sequence
from typing import override

from app import constants
from app.interfaces import UserPrompt
from app.menu import MenuAction
from app.quit_requested import QuitRequested

from .portal_action import PortalAction


class HealthcarePortal(MenuAction):

    def __init__(
        self, prompt: UserPrompt, actions: Sequence[PortalAction]
    ) -> None:
        super().__init__(constants.HEALTHCARE_PORTAL_LABEL)
        self.__prompt = prompt
        self.__actions = list(actions)

    @override
    def run(self) -> bool:
        action = self.__prompt.choose(self.__actions, quittable=True)
        if action is None:
            return True
        try:
            error = action.run()
        except QuitRequested:
            return True
        if error:
            self.__prompt.show_message(error)
        return True
