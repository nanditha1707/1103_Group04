from collections.abc import Iterable
from typing import override

from io_manager.console import Console


class FakeConsole(Console):
    def __init__(
        self, inputs: Iterable[str] = (), width: int = 250
    ) -> None:
        self.__inputs = list(inputs)
        self.__width = width
        self.__prompts: list[str] = []
        self.__shown: list[str] = []

    @property
    def prompts(self) -> list[str]:
        return list(self.__prompts)

    @property
    def shown(self) -> list[str]:
        return list(self.__shown)

    @override
    def ask(self, prompt: str) -> str:
        self.__prompts.append(prompt)
        if not self.__inputs:
            raise AssertionError(f"No scripted input left for the prompt: {prompt}")
        return self.__inputs.pop(0)

    @override
    def show(self, text: str) -> None:
        self.__shown.append(text)

    @override
    def width(self) -> int:
        return self.__width
