from typing import override

from app import constants
from app.interfaces import UserPrompt
from app.queries import PatientQueryHandler

from .portal_action import PortalAction


class PastPatientQuery(PortalAction):

    def __init__(
        self, prompt: UserPrompt, query_handler: PatientQueryHandler
    ) -> None:
        super().__init__(constants.PAST_PATIENT_QUERY_LABEL)
        self.__prompt = prompt
        self.__query_handler = query_handler

    @override
    def run(self) -> str | None:
        date = self.__prompt.ask_date(constants.DATE_PROMPT)
        if date is None:
            return None
        return self.__query_handler.handle(date)
