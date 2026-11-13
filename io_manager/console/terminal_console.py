from typing import override
import shutil

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

    @override
    def width(self) -> int:
        return shutil.get_terminal_size().columns
