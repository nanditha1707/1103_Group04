from typing import override

from app import constants
from data_manager import DataManager

from .report import Report


class PatientTypeBreakdownReport(Report):

    def __init__(
        self, data: DataManager
    ) -> None:
        super().__init__(constants.PATIENT_TYPE_BREAKDOWN_LABEL, constants.PATIENT_TYPE_BREAKDOWN_HEADER)
        self.__data = data

    @override
    def fetch(self, date: str) -> dict[str, int] | None:
        return self.__data.get_patient_type_breakdown(date)
