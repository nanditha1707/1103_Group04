from collections.abc import Sequence
from typing import override

from app import constants
from app.menu import MenuAction
from io_manager import IOManager

from .portal_action import PortalAction


class HealthcarePortal(MenuAction):

    def __init__(
        self, io: IOManager, actions: Sequence[PortalAction]
    ) -> None:
        super().__init__(constants.HEALTHCARE_PORTAL_LABEL)
        self.__io = io
        self.__actions = list(actions)

    @override
    def run(self) -> bool:
        action = self.__io.choose(self.__actions)
        if action is not None:
            error = action.run()
            if error:
                self.__io.show_message(error)
        return True
