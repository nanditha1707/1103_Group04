from collections.abc import Sequence
from typing import override

from app import constants
from app.reports import Report
from io_manager import IOManager

from .portal_action import PortalAction


class ReportMenu(PortalAction):

    def __init__(
        self, io: IOManager, reports: Sequence[Report]
    ) -> None:
        super().__init__(constants.REPORTS_LABEL)
        self.__io = io
        self.__reports = list(reports)

    @override
    def run(self) -> str | None:
        report = self.__io.choose(self.__reports, constants.REPORT_MENU_HEADER)
        if report is None:
            return None

        date = self.__io.ask(constants.DATE_PROMPT).strip()
        error = self.__io.validate_date(date)
        if error is not None:
            return error

        result = report.fetch(date)
        # A valid report returns None only if the database failed.
        if result is None:
            return constants.DATABASE_ERROR_MESSAGE
        # An empty report means nothing matched the date.
        if not result:
            return constants.NO_MATCHING_RECORDS_MESSAGE

        self.__io.show_table(result, report.header)
        return None
