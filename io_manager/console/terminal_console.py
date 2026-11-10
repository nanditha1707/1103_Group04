from typing import override

from .console import Console


class TerminalConsole(Console):
    """
    Console that reads from and writes to the terminal.

    This is the only class in the IO package that actually calls input() or
    print() and gives the console interface its implementation.
    """

    @override
    def ask(self, prompt: str) -> str:
        return input(prompt)

    @override
    def show(self, text: str) -> None:
        print(text)