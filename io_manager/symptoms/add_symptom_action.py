from abc import ABC, abstractmethod
from typing import override

from io_manager import messages
from io_manager.console.console import Console
from io_manager.symptoms.symptom_menu_action import SymptomMenuAction


class AddSymptomAction(SymptomMenuAction, ABC):
    """
    Abstract subclass for actions that add a symptom to the list.

    Execute is fixed here: choose a symptom, then add it if it is not a duplicate. 
    Subclasses only decide how the symptom is chosen.
    The execute method here is final and is not overriden by any subclasses.
    The subclasses only need to implement the _choose method, 
    which returns the symptom to add, or None to add nothing.
    """

    @override
    def execute(self, console: Console, symptoms: list[str]) -> bool:
        symptom = self._choose(console)
        if symptom:
            self.__add_unique(console, symptoms, symptom)
        # Returns false to ensure menu continues running, 
        # as adding a symptom should not exit the menu.
        return False

    @abstractmethod
    def _choose(self, console: Console) -> str | None:
        """Returns the symptom to add, or None if no symptom was selected."""

    @staticmethod
    def __add_unique(console: Console, symptoms: list[str], symptom: str) -> None:
    # Guards against adding duplicate symptoms to the list.
        if symptom in symptoms:
            console.show(messages.DUPLICATE_SYMPTOM_ERROR)
            return
        symptoms.append(symptom)
