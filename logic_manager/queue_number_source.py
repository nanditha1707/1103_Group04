from typing import Protocol


class QueueNumberSource(Protocol):
    """
    Anything that can tell QueueNumberGenerator the highest queue number
    already given out in a queue on a date.

    This is a Protocol rather than an ABC so data_manager never has to
    import or subclass it. Any object with a matching
    get_highest_queue_number method fits, and main.py passes data_manager in.
    """

    def get_highest_queue_number(self, prefix: str, date: str) -> int | None:
        """
        Return the highest number in the queue on the date, e.g. 7 for D007.
        Return 0 if the queue has no numbers yet, or None if the records
        could not be read.
        """
