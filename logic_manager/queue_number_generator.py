from .queue_number_source import QueueNumberSource
from .route import Route

class QueueNumberGenerator:
    """
    Gives out the next queue number for a date, e.g. D008, by asking the
    QueueNumberSource for the highest number already given out.
    """

    # Letter at the start of each queue number to differentiate.
    _PREFIXES = {
        Route.EMERGENCY: "U",
        Route.DOCTOR: "D",
        Route.PHARMACIST: "P",
        Route.RETAIL: "PR"
    }

    def __init__(
        self, queue_numbers: QueueNumberSource
    ):
        self.__queue_numbers = queue_numbers

    def next_number(self, route: Route, date: str) -> str:
        """
        Return the next queue number for the route on the given date, e.g. D008.
        The queue starts from 001 if the records could not be read.
        """
        prefix = self._PREFIXES[route]
        highest_number = self.__queue_numbers.get_highest_queue_number(prefix, date)

        if highest_number is None:
            highest_number = 0

        next_number = highest_number + 1

        # :03d sets the minimum width to 3, so instead of D9 it is D009.
        return f"{prefix}{next_number:03d}"
