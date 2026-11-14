from typing import override

from app import constants

from .menu_action import MenuAction
from .password_gate import PasswordGate


class PasswordProtectedAction(MenuAction):
    """
    Wraps a main menu option so it only runs after the admin password is entered.
    A wrong password goes back to the main menu.
    """

    def __init__(
        self, action: MenuAction, gate: PasswordGate
    ) -> None:
        super().__init__(action.label)
        self.__action = action
        self.__gate = gate

    @override
    def run(self) -> bool:
        if not self.__gate.unlock(constants.ADMIN_PASSWORD_PROMPT):
            return True
        return self.__action.run()
