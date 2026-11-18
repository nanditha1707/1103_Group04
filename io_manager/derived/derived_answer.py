from abc import ABC, abstractmethod

from io_manager.patient_answers import PatientAnswers
from typedefs import Answer


class DerivedAnswer(ABC):
    """
    Interface for an answer the patient is not asked for directly but
    is worked out from their other answers, e.g. age from birthdate.

    RegistrationForm recalculates every derived answer each time an
    answer is saved so it always matches the answers it comes from.
    """

    def __init__(
        self, key: str, share_with_ai: bool = False
    ) -> None:
        self.__key = key
        self.__share_with_ai = share_with_ai

    @property
    def key(self) -> str:
        """
        The key the derived answer is stored under, e.g. "age".
        """
        return self.__key

    @property
    def share_with_ai(self) -> bool:
        """
        Return True if the derived answer is to be sent to the AI.
        """
        return self.__share_with_ai

    @abstractmethod
    def compute(self, answers: PatientAnswers) -> Answer:
        """
        Return the derived answer or None if the answers it comes from
        have not been given yet.
        """
