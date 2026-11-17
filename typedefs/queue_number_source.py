from typing import Protocol


class QueueNumberSource(Protocol):
    """
    Anything that can tell QueueNumberGenerator the highest queue number
    already given out in a queue on a date.

    It is kept in typedefs so logic_manager, which asks for queue numbers,
    and data_manager, which provides them, share one definition without
    importing each other. It is a Protocol, so any object with a matching
    get_highest_queue_number method fits. ApplicationFactory passes the
    DataManager in.
    """

    def get_highest_queue_number(self, prefix: str, date: str) -> int | None:
        """
        Return the highest number in the queue on the date, e.g. 7 for D007.
        Return 0 if the queue has no numbers yet, or None if the records
        could not be read.
        """
        pass
