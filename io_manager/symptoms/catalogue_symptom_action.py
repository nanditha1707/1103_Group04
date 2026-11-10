from typing import override

from io_manager import messages
from io_manager.console.console import Console
from io_manager.symptoms.add_symptom_action import AddSymptomAction
from io_manager.symptoms.symptom_catalogue import SymptomCatalogue
from io_manager.symptoms.yes_no_prompt import YesNoPrompt


class CatalogueSymptomAction(AddSymptomAction):
    """
    Accepts user input and checks it against the symptom catalogue. 
    If the input matches a known symptom, it is returned. 
    If the input is close to a known symptom, the user is prompted to confirm if that was their intended symptom. 
    If the input does not match any known symptoms, an error message is displayed.
    """

    def __init__(
        self, catalogue: SymptomCatalogue, yes_no_prompt: YesNoPrompt
    ) -> None:
        super().__init__(messages.OTHER_SYMPTOMS_LABEL)
        self.__catalogue = catalogue
        self.__yes_no_prompt = yes_no_prompt

    @override
    def _choose(self, console: Console) -> str | None:
        text = console.ask_normalised(messages.SYMPTOM_ENTRY_PROMPT)
        if not text:
            console.show(messages.EMPTY_INPUT_ERROR)
            return None

        matched, is_exact = self.__catalogue.match(text)
        if matched is None:
            console.show(messages.SYMPTOM_NOT_FOUND)
            return None
        if is_exact:
            return matched

        # For a close match, the patient checks to confirm if it is what they meant.
        prompt = messages.SYMPTOM_CONFIRM_PROMPT.format(symptom=matched)
        if self.__yes_no_prompt.confirm(console, prompt):
            return matched
        # If they say it is not, no symptom is returned.
        return None
