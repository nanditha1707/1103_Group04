from password_hasher import PasswordHasher
from user import User
from user_repository import UserRepository

class AuthService:
    """Validates healthcare professional login credentials."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher | None = None,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher or PasswordHasher()
    
    def authenticate(self, nric: str, password: str) -> User | None:
        """Return the authenticated User if NRIC and password match, else None."""
        normalized_nric = nric.strip().upper()
        if not normalized_nric or not password:
            return None

        user = self._user_repository.get_by_nric(normalized_nric)
        if user is None:
            return None

        if not self._password_hasher.verify(password, user.password_hash):
            return None

        return user

    