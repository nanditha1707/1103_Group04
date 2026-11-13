from collections.abc import Mapping
from typing import Protocol

from io_manager.patient_answers import Answer


class RegistrationScreens(Protocol):

    def collect_registration(self) -> dict[str, Answer] | None:
        pass

    def filter_for_ai(self, answers: Mapping[str, Answer]) -> dict[str, Answer]:
        pass

    def show_result(self, ai_output: Mapping[str, object], logic_result: Mapping[str, str | None]) -> None:
        pass
