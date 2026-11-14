from collections.abc import Sequence
from typing import override

from app import constants
from app.interfaces import TableDisplay, UserPrompt
from app.reports import Report

from .portal_action import PortalAction


class ReportMenu(PortalAction):

    def __init__(
        self, prompt: UserPrompt, tables: TableDisplay, reports: Sequence[Report]
    ) -> None:
        super().__init__(constants.REPORTS_LABEL)
        self.__prompt = prompt
        self.__tables = tables
        self.__reports = list(reports)

    @override
    def run(self) -> str | None:
        report = self.__prompt.choose(self.__reports, constants.REPORT_MENU_HEADER)
        if report is None:
            return None

        date = self.__prompt.ask_date(constants.DATE_PROMPT)
        if date is None:
            return None

        result = report.fetch(date)
        # A valid report returns None only if the database failed.
        if result is None:
            return constants.DATABASE_ERROR_MESSAGE
        # An empty report means nothing matched the date.
        if not result:
            return constants.NO_MATCHING_RECORDS_MESSAGE

        self.__tables.show_table(result, report.header)
        return None
