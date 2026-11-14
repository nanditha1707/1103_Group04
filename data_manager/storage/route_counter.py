from abc import ABC, abstractmethod

class RouteCounter(ABC):
    """
    Interface for counting how many patients took each route on a date.
    The route column is not encrypted, so the database can count it directly.
    """

    @abstractmethod
    def count_each_route(self, date: str) -> dict[str, int] | None:
        """Return how many patients took each route on the date,
        or None if the records could not be read."""
