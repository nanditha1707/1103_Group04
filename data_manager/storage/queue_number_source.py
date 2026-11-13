from abc import ABC, abstractmethod


class QueueNumberSource(ABC):
    @abstractmethod
    def get_highest_queue_number(self, prefix: str, date: str) -> int | None:
        pass
