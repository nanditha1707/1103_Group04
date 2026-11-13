from typing import Protocol

import pandas as pd


class PatientRecords(Protocol):

    def get_current_date(self) -> str:
        pass

    def get_patient_by_queue(self, queue_number: str, filter_columns: list[str], date: str) -> pd.DataFrame | None:
        pass

    def get_patients_by_date(self, filter_columns: list[str], date: str) -> pd.DataFrame | None:
        pass

    def export_query(self, query_df: pd.DataFrame) -> bool:
        pass
