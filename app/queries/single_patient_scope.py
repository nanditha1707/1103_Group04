from typing import override

import pandas as pd

from app import constants
from app.interfaces import PatientRecords

from .query_scope import QueryScope


class SinglePatientScope(QueryScope):

    def __init__(
        self, records: PatientRecords
    ) -> None:
        super().__init__(constants.SINGLE_PATIENT_LABEL, constants.PATIENT_NOT_FOUND_MESSAGE, constants.QUEUE_NUMBER_PROMPT)
        self.__records = records

    @override
    def fetch(self, filter_columns: list[str], date: str, detail: str) -> pd.DataFrame | None:
        return self.__records.get_patient_by_queue(detail.strip().upper(), filter_columns, date)
