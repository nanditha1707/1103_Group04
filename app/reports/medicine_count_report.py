from typing import override

from app import constants
from app.interfaces import ReportSource, UserPrompt
from app.quit_requested import QuitRequested

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
        medicine = self.__prompt.ask_or_quit(constants.MEDICINE_PROMPT)
        if medicine is None:
            raise QuitRequested
        return self.__source.get_medicine_count(medicine.strip().upper(), date)
