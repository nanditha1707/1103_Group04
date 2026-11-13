from typing import override

from app import constants
from app.interfaces import PatientRecords
from app.queries import PatientQueryHandler

from .portal_action import PortalAction


class CurrentPatientQuery(PortalAction):

    def __init__(
        self, records: PatientRecords, query_handler: PatientQueryHandler
    ) -> None:
        super().__init__(constants.CURRENT_PATIENT_QUERY_LABEL)
        self.__records = records
        self.__query_handler = query_handler

    @override
    def run(self) -> str | None:
        return self.__query_handler.handle(self.__records.get_current_date())
