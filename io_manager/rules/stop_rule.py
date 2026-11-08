from abc import ABC, abstractmethod

from io_manager.patient_answers import PatientAnswers


class StopRule(ABC):
    """Interface for deciding whether the registration process should stop, 
    based on the answers given."""

    @abstractmethod
    def stop_message(self, answers: PatientAnswers) -> str | None:
        """Returns the stop message to show if registration must stop,
        otherwise it returns None."""