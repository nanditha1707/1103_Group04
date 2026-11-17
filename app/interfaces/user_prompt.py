from collections.abc import Sequence
from typing import Protocol

from typedefs import Labelled


class UserPrompt(Protocol):

    def ask_or_quit(self, prompt: str) -> str | None:
        pass

    def show_message(self, message: str) -> None:
        pass

    def choose(self, options: Sequence[Labelled], header: str | None = None, quittable: bool = False) -> Labelled | None:
        pass

    def ask_date(self, prompt: str) -> str | None:
        pass
