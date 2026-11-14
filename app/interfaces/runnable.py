from typing import Protocol


class Runnable(Protocol):
    """Anything main.py can start with run(), either the Application or a
    StartupFailure that shows why the program could not start.

    Used as the return type of ApplicationFactory.create() which returns a
    StartupFailure if the encryption key, database or admin password check
    fails and the Application otherwise. main.py then calls run() on it."""

    def run(self) -> None:
        pass
