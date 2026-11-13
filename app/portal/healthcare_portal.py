from collections.abc import Sequence
from typing import override

from app import constants
from app.interfaces import UserPrompt
from app.menu import MenuAction

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
        action = self.__prompt.choose(self.__actions)
        if action is not None:
            error = action.run()
            if error:
                self.__prompt.show_message(error)
        return True
