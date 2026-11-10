from typing import override

from io_manager.console import Console
from io_manager.symptoms.add_symptom_action import AddSymptomAction


class PresetSymptomAction(AddSymptomAction):
    """
    Used to add a preset symptom to the list of symptoms. 
    Specifically for preset symptoms that do not require a follow-up question, 
    such as Cough or Heaadache.
    """
    
    def __init__(
        self, label: str, symptom: str
    ) -> None:
        super().__init__(label)
        self.__symptom = symptom

    @override
    def _choose(self, console: Console) -> str:
        return self.__symptom
