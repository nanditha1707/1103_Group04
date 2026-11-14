from typing import Protocol


class Runnable(Protocol):
    """Anything main.py can start with run(), either the Application or a
    StartupFailure that shows why the program could not start."""

    def run(self) -> None:
        pass
