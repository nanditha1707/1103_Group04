from collections.abc import Sequence
from typing import override

from app import constants
from app.numbered_options import NumberedOptions
from app.reports import Report
from io_manager import IOManager

from .portal_action import PortalAction


class ReportMenu(PortalAction):

    def __init__(
        self, io: IOManager, reports: Sequence[Report]
    ) -> None:
        super().__init__(constants.REPORTS_LABEL)
        self.__io = io
        self.__reports = NumberedOptions(reports)

    @override
    def run(self) -> str | None:
        choice = self.__io.prompt_menu(self.__reports.lines(), constants.REPORT_MENU_HEADER)
        error = self.__io.validate_option(choice, len(self.__reports))
        if error is not None:
            return error

        date = self.__io.ask(constants.DATE_PROMPT).strip()
        error = self.__io.validate_date(date)
        if error is not None:
            return error

        report = self.__reports.find(choice)
        if report is None:
            return constants.INVALID_OPTION_NUMBER_MESSAGE

        result = report.fetch(date)
        # A valid report returns None only if the database failed.
        if result is None:
            return constants.DATABASE_ERROR_MESSAGE
        # An empty report means nothing matched the date.
        if not result:
            return constants.NO_MATCHING_RECORDS_MESSAGE

        self.__io.show_table(result, report.header)
        return None
