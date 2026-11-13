from typing import Protocol


class ReportSource(Protocol):

    def get_medicine_count(self, medicine: str, date: str) -> dict[str, int] | None:
        pass

    def get_medicine_breakdown(self, date: str) -> dict[str, int] | None:
        pass

    def get_patient_type_breakdown(self, date: str) -> dict[str, int] | None:
        pass
