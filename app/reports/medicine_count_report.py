from typing import override

from app import constants
from data_manager import DataManager
from io_manager import IOManager

from .report import Report


class MedicineCountReport(Report):

    def __init__(
        self, io: IOManager, data: DataManager
    ) -> None:
        super().__init__(constants.MEDICINE_COUNT_LABEL, constants.MEDICINE_COUNT_HEADER)
        self.__io = io
        self.__data = data

    @override
    def fetch(self, date: str) -> dict[str, int] | None:
        medicine = self.__io.ask(constants.MEDICINE_PROMPT).strip().upper()
        return self.__data.get_medicine_count(medicine, date)
