from abc import ABC, abstractmethod

import pandas as pd


class RecordReader(ABC):
    @abstractmethod
    def find_by_queue(self, queue_number: str, columns: list[str], date: str) -> pd.DataFrame | None:
        pass

    @abstractmethod
    def find_by_date(self, columns: list[str], date: str) -> pd.DataFrame | None:
        pass
