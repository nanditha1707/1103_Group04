from abc import ABC, abstractmethod

from io_manager.patient_answers import PatientAnswers


class SkipRule(ABC):
    """
    Interface for whether a question should be skipped, 
    based on the patient's given responses.
    """

    @abstractmethod
    def should_skip(self, answers: PatientAnswers) -> bool:
        """Return True if the question should be skipped."""