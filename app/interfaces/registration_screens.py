from collections.abc import Mapping
from typing import Protocol

from typedefs import Answer


class RegistrationScreens(Protocol):

    def collect_registration(self) -> dict[str, Answer] | None:
        pass

    def filter_for_ai(self, answers: Mapping[str, Answer]) -> dict[str, Answer]:
        pass

    def show_result(self, logic_result: Mapping[str, str | None]) -> None:
        pass
