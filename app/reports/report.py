from abc import abstractmethod

from app.menu_option import MenuOption


class Report(MenuOption):
    """
    One report in the report menu.

    fetch only reads the records and never asks the user anything.
    A report that needs one more answer first, such as a medicine name, gives its question as detail_prompt.
    ReportMenu asks that question and passes the answer to fetch, so every report is used the same way.
    """

    def __init__(
        self, label: str, header: str, detail_prompt: str | None = None
    ) -> None:
        super().__init__(label)
        self.__header = header
        self.__detail_prompt = detail_prompt

    @property
    def header(self) -> str:
        return self.__header

    @property
    def detail_prompt(self) -> str | None:
        """
        The question to ask before fetch, or None if the report needs nothing else.
        """
        return self.__detail_prompt

    @abstractmethod
    def fetch(self, date: str, detail: str) -> dict[str, int] | None:
        """
        Return the report for the date, which is empty if nothing matched,
        or None if the database could not be reached.
        """
