from typing import override

from app import constants
from app.interfaces import ReportSource

from .report import Report


class MedicineBreakdownReport(Report):

    def __init__(
        self, source: ReportSource
    ) -> None:
        super().__init__(constants.MEDICINE_BREAKDOWN_LABEL, constants.MEDICINE_BREAKDOWN_HEADER)
        self.__source = source

    @override
    def fetch(self, date: str) -> dict[str, int] | None:
        return self.__source.get_medicine_breakdown(date)
