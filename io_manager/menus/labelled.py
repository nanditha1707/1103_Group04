from typing import Protocol


class Labelled(Protocol):

    @property
    def label(self) -> str:
        pass
