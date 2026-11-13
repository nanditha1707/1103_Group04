from abc import ABC


class MenuOption(ABC):

    def __init__(
        self, label: str
    ) -> None:
        self.__label = label

    @property
    def label(self) -> str:
        return self.__label
