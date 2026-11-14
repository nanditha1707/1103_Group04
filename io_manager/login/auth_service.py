from typing import Optional

from .password_hasher import PasswordHasher
from .user import User
from .user_repository import UserRepository


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: Optional[PasswordHasher] = None,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher or PasswordHasher()
