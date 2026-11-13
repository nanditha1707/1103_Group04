from typing import override

from io_manager import constants
from io_manager.console import Console
from .symptom_menu_action import SymptomMenuAction


class DoneAction(SymptomMenuAction):
    """
    Finishes the symptom menu, allowing the symptom menu to be exited,
    but only once at least one symptom has been entered.
    """

    def __init__(
        self
    ) -> None:
        super().__init__(constants.DONE_LABEL)

    @override
    def execute(self, console: Console, symptoms: list[str]) -> bool:
        # Check if there are any symptoms entered
        if not symptoms:
            console.show(constants.NO_SYMPTOMS_ERROR)
            return False
        # Return True to indicate that the symptom menu should be exited
        return True
