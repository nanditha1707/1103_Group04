from typing import override

from app import constants
from data_manager import DataManager

from .report import Report


class MedicineBreakdownReport(Report):

    def __init__(
        self, data: DataManager
    ) -> None:
        super().__init__(constants.MEDICINE_BREAKDOWN_LABEL, constants.MEDICINE_BREAKDOWN_HEADER)
        self.__data = data

    @override
    def fetch(self, date: str) -> dict[str, int] | None:
        return self.__data.get_medicine_breakdown(date)
