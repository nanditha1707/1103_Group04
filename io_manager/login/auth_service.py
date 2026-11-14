from .password_hasher import PasswordHasher
from .user_repository import UserRepository


class AuthService:
    """Validates healthcare professional login credentials."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher | None = None,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher or PasswordHasher()

    