from typing import override

import pandas as pd

from app import constants
from data_manager import DataManager

from .query_scope import QueryScope


class AllPatientsScope(QueryScope):

    def __init__(
        self, data: DataManager
    ) -> None:
        super().__init__(constants.ALL_PATIENTS_LABEL, constants.NO_PATIENTS_ON_DATE_MESSAGE)
        self.__data = data

    @override
    def fetch(self, filter_columns: list[str], date: str) -> pd.DataFrame | None:
        return self.__data.get_patients_by_date(filter_columns, date)
