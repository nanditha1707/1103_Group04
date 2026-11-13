from collections.abc import Sequence
from typing import override

from app import constants
from app.menu import MenuAction
from app.numbered_options import NumberedOptions
from io_manager import IOManager

from .portal_action import PortalAction


class HealthcarePortal(MenuAction):

    def __init__(
        self, io: IOManager, actions: Sequence[PortalAction]
    ) -> None:
        super().__init__(constants.HEALTHCARE_PORTAL_LABEL)
        self.__io = io
        self.__actions = NumberedOptions(actions)

    @override
    def run(self) -> bool:
        choice = self.__io.prompt_menu(self.__actions.lines())
        error = self.__io.validate_option(choice, len(self.__actions))
        if error is None:
            action = self.__actions.find(str(int(choice)))
            if action is None:
                error = constants.INVALID_OPTION_NUMBER_MESSAGE
            else:
                error = action.run()
        if error:
            self.__io.show_message(error)
        return True
