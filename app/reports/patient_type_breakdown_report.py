from typing import override

from app import constants
from app.interfaces import ReportSource

from .report import Report


class PatientTypeBreakdownReport(Report):

    def __init__(
        self, source: ReportSource
    ) -> None:
        super().__init__(constants.PATIENT_TYPE_BREAKDOWN_LABEL, constants.PATIENT_TYPE_BREAKDOWN_HEADER)
        self.__source = source

    @override
    def fetch(self, date: str) -> dict[str, int] | None:
        return self.__source.get_patient_type_breakdown(date)
