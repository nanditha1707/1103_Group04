from abc import ABC, abstractmethod

from user import User


class UserRepository(ABC):

    @abstractmethod
    def get_by_nric(self, nric: str) -> User | None:
        """Return a User matching the NRIC, or None if not found."""
        raise NotImplementedError