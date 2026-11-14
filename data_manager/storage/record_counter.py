from abc import ABC, abstractmethod


class RecordCounter(ABC):
    @abstractmethod
    def count_medicine(self, medicine: str, date: str) -> int | None:
        """Return how many times the medicine was issued on the date."""

    @abstractmethod
    def count_each_medicine(self, date: str) -> dict[str, int] | None:
         """Return each medicine issued on the date with its count, 
         ordered by descending order."""

    @abstractmethod
    def count_each_route(self, date: str) -> dict[str, int] | None:
        """Return how many patients took each route on the date."""
