from abc import ABC, abstractmethod
from typing import Optional

from .user import User


class UserRepository(ABC):
    @abstractmethod
    def get_by_nric(self, nric: str) -> Optional[User]:
        raise NotImplementedError