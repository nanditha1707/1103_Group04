from abc import abstractmethod

import pandas as pd

from app.menu_option import MenuOption


class QueryScope(MenuOption):
    """
    Which patients a query looks up, e.g. one patient or every patient on a date.

    fetch only reads the records and never asks the user anything.
    A scope that needs one more answer first, such as a queue number, gives its question as detail_prompt.
    PatientQueryHandler asks that question and passes the answer to fetch, so every scope is used the same way.
    """

    def __init__(
        self, label: str, not_found_error: str, detail_prompt: str | None = None
    ) -> None:
        super().__init__(label)
        self.__not_found_error = not_found_error
        self.__detail_prompt = detail_prompt

    @property
    def not_found_error(self) -> str:
        return self.__not_found_error

    @property
    def detail_prompt(self) -> str | None:
        """
        The question to ask before fetch, or None if the scope needs nothing else.
        """
        return self.__detail_prompt

    @abstractmethod
    def fetch(self, filter_columns: list[str], date: str, detail: str) -> pd.DataFrame | None:
        """
        Return the matching records with only the filter_columns, which is empty if none match,
        or None if the database could not be reached.
        """
        pass
