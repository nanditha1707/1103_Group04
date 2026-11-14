from collections.abc import Sequence

from app.menu_option import MenuOption


class QueryFilter(MenuOption):

    def __init__(
        self, label: str, columns: Sequence[str]
    ) -> None:
        super().__init__(label)
        self.__columns = list(columns)

    @property
    def columns(self) -> list[str]:
        return list(self.__columns)
