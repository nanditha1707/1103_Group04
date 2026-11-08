from abc import ABC, abstractmethod

from io_manager.answer_sheet import AnswerSheet


class StopRule(ABC):
    """Interface for deciding whether the registration process should stop, 
    based on the answers given."""

    @abstractmethod
    def stop_message(self, answers: AnswerSheet) -> str | None:
        """Returns the stop message to show if registration must stop,
        otherwise it returns None."""