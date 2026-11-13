from abc import ABC, abstractmethod


class RecordWriter(ABC):
    @abstractmethod
    def save(self, record: dict) -> str | None:
        pass
