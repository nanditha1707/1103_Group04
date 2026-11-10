from typing import override

from io_manager import messages
from io_manager.console.console import Console
from io_manager.symptoms.add_symptom_action import AddSymptomAction
from io_manager.symptoms.yes_no_prompt import YesNoPrompt


class FeverSymptomAction(AddSymptomAction):
    """
    Follow up for the FEVER symptom.
    The prompt asks if their temperature is 39.0 °C or higher, 
    and if the user confirms, HIGH FEVER is added. 
    Otherwise, FEVER is added. 
    """

    HIGH_FEVER = "HIGH FEVER"
    FEVER = "FEVER"

    def __init__(
        self, yes_no_prompt: YesNoPrompt
    ) -> None:
        super().__init__(messages.FEVER_LABEL)
        self.__yes_no_prompt = yes_no_prompt

    @override
    def _choose(self, console: Console) -> str:
        if self.__yes_no_prompt.confirm(console, messages.FEVER_PROMPT):
            return self.HIGH_FEVER
        return self.FEVER
