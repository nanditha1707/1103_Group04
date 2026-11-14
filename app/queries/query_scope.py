from abc import abstractmethod

import pandas as pd

from app.menu_option import MenuOption


class QueryScope(MenuOption):

    def __init__(
        self, label: str, not_found_error: str
    ) -> None:
        super().__init__(label)
        self.__not_found_error = not_found_error

    @property
    def not_found_error(self) -> str:
        return self.__not_found_error

    @abstractmethod
    def fetch(self, filter_columns: list[str], date: str) -> pd.DataFrame | None:
        pass
