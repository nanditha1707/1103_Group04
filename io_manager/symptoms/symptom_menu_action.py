from abc import ABC, abstractmethod

from io_manager.console.console import Console

class SymptomMenuAction(ABC):
    """
    Abstract class for actions that can be performed on a list of symptoms. 
    Each action has a label, which is shown in the menu, and an execute method, 
    which performs the action tagged to it relating to symptoms.
    These can range from adding fixed symptoms, removing symptoms, or even exiting the symptom menu.
    """

    def __init__(
        self, label: str
    ) -> None:
        self.__label = label

    @property
    def label(self) -> str:
        # Returns the menu line text
        return self.__label

    @abstractmethod
    def execute(self, console: Console, symptoms: list[str]) -> bool:
        """
        Run the action on the menu's working list of symptoms, 
        which it may change in place. 
        Return True only occurs when the patient is finished with the menu.
        """
