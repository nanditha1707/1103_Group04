from collections.abc import Sequence
from typing import Protocol

from io_manager.menus import Labelled


class UserPrompt(Protocol):

    def ask(self, prompt: str) -> str:
        pass

    def show_message(self, message: str) -> None:
        pass

    def choose(self, options: Sequence[Labelled], header: str | None = None) -> Labelled | None:
        pass

    def ask_date(self, prompt: str) -> str | None:
        pass
