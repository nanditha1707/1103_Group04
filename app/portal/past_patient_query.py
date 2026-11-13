from typing import override

from app import constants
from app.queries import PatientQueryHandler
from io_manager import IOManager

from .portal_action import PortalAction


class PastPatientQuery(PortalAction):

    def __init__(
        self, io: IOManager, query_handler: PatientQueryHandler
    ) -> None:
        super().__init__(constants.PAST_PATIENT_QUERY_LABEL)
        self.__io = io
        self.__query_handler = query_handler

    @override
    def run(self) -> str | None:
        date = self.__io.ask(constants.DATE_PROMPT).strip()
        error = self.__io.validate_date(date)
        if error is None:
            error = self.__query_handler.handle(date)
        return error
