from abc import ABC, abstractmethod


class RecordCounter(ABC):
    @abstractmethod
    def count_medicine(self, medicine: str, date: str) -> int | None:
        pass

    @abstractmethod
    def count_each_medicine(self, date: str) -> dict[str, int] | None:
        pass

    @abstractmethod
    def count_each_route(self, date: str) -> dict[str, int] | None:
        pass
