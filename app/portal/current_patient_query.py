from typing import override

from app import constants
from app.queries import PatientQueryHandler
from data_manager import DataManager

from .portal_action import PortalAction


class CurrentPatientQuery(PortalAction):

    def __init__(
        self, data: DataManager, query_handler: PatientQueryHandler
    ) -> None:
        super().__init__(constants.CURRENT_PATIENT_QUERY_LABEL)
        self.__data = data
        self.__query_handler = query_handler

    @override
    def run(self) -> str | None:
        return self.__query_handler.handle(self.__data.get_current_date())
