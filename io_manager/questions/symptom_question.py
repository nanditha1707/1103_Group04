from typing import override

from io_manager.console.console import Console
from io_manager.navigation.question_result import QuestionResult
from io_manager.patient_answers import Answer
from io_manager.questions.question import Question
from io_manager.symptoms.symptom_menu import SymptomMenu


class SymptomQuestion(Question):
    """
    The symptoms question, answered through the symptom menu
    (aggregation) instead of one typed line.
    """

    def __init__(
        self, key: str, prompt: str, menu: SymptomMenu, share_with_ai: bool = False
    ) -> None:
        super().__init__(key, prompt, share_with_ai)
        self.__menu = menu

    @override
    def ask(self, console: Console, previous: Answer) -> QuestionResult:
        # The menu starts from the earlier symptoms, so going back to
        # this question keeps what the patient already entered.
        # previous is None the first time this question is asked.
        starting = previous or []
        return self.__menu.run(console, starting)

    @override
    def display_value(self, value: Answer) -> str:
        # Always a non-empty list here: this question is never skipped
        # and the menu's Done option refuses an empty list.
        return ", ".join(value)