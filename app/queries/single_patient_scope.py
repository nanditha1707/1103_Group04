from typing import override

import pandas as pd

from app import constants
from app.interfaces import PatientRecords, UserPrompt
from app.quit_requested import QuitRequested

from .query_scope import QueryScope


class SinglePatientScope(QueryScope):

    def __init__(
        self, prompt: UserPrompt, records: PatientRecords
    ) -> None:
        super().__init__(constants.SINGLE_PATIENT_LABEL, constants.PATIENT_NOT_FOUND_MESSAGE)
        self.__prompt = prompt
        self.__records = records

    @override
    def fetch(self, filter_columns: list[str], date: str) -> pd.DataFrame | None:
        queue = self.__prompt.ask_or_quit(constants.QUEUE_NUMBER_PROMPT)
        if queue is None:
            raise QuitRequested
        return self.__records.get_patient_by_queue(queue.strip().upper(), filter_columns, date)
