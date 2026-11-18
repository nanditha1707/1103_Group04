from abc import abstractmethod

from .route_counter import RouteCounter


class RecordCounter(RouteCounter):
    """Counts every daily report figure. Adds the medicine counts to the
    route count from RouteCounter."""

    @abstractmethod
    def count_medicine(self, medicine: str, date: str) -> int | None:
        """Return how many times the medicine was issued on the date."""

    @abstractmethod
    def count_each_medicine(self, date: str) -> dict[str, int] | None:
         """Return each medicine issued on the date with its count, 
         ordered by descending order."""
