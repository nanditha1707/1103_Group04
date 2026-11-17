from typing import override

from app import constants
from app.interfaces import ReportSource

from .report import Report


class MedicineCountReport(Report):

    def __init__(
        self, source: ReportSource
    ) -> None:
        super().__init__(constants.MEDICINE_COUNT_LABEL, constants.MEDICINE_COUNT_HEADER, constants.MEDICINE_PROMPT)
        self.__source = source

    @override
    def fetch(self, date: str, detail: str) -> dict[str, int] | None:
        return self.__source.get_medicine_count(detail.strip().upper(), date)
