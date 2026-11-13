from typing import override

from app import constants
from app.interfaces import ReportSource, UserPrompt

from .report import Report


class MedicineCountReport(Report):

    def __init__(
        self, prompt: UserPrompt, source: ReportSource
    ) -> None:
        super().__init__(constants.MEDICINE_COUNT_LABEL, constants.MEDICINE_COUNT_HEADER)
        self.__prompt = prompt
        self.__source = source

    @override
    def fetch(self, date: str) -> dict[str, int] | None:
        medicine = self.__prompt.ask(constants.MEDICINE_PROMPT).strip().upper()
        return self.__source.get_medicine_count(medicine, date)
