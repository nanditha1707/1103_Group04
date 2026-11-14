from abc import abstractmethod

from app.menu_option import MenuOption


class Report(MenuOption):

    def __init__(
        self, label: str, header: str
    ) -> None:
        super().__init__(label)
        self.__header = header

    @property
    def header(self) -> str:
        return self.__header

    @abstractmethod
    def fetch(self, date: str) -> dict[str, int] | None:
        pass
