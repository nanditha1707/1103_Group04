from typing import override

import pandas as pd

from app import constants
from data_manager import DataManager
from io_manager import IOManager

from .query_scope import QueryScope


class SinglePatientScope(QueryScope):

    def __init__(
        self, io: IOManager, data: DataManager
    ) -> None:
        super().__init__(constants.SINGLE_PATIENT_LABEL, constants.PATIENT_NOT_FOUND_MESSAGE)
        self.__io = io
        self.__data = data

    @override
    def fetch(self, filter_columns: list[str], date: str) -> pd.DataFrame | None:
        queue = self.__io.ask(constants.QUEUE_NUMBER_PROMPT).strip().upper()
        return self.__data.get_patient_by_queue(queue, filter_columns, date)
