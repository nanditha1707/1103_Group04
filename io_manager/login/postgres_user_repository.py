from data_manager.storage import Database

from .user import User
from .user_repository import UserRepository


class PostgresUserRepository(UserRepository):
    """Retrieves healthcare professional login details from PostgreSQL."""

    def __init__(self, database: Database):
        self.__database = database

    def get_by_nric(self, nric: str) -> User | None:
        """Return the user matching the NRIC, or None if not found."""

        query = """
            SELECT nric, password_hash, role
            FROM users
            WHERE nric = %s
        """

        rows = self.__database.fetch_rows(query, (nric,))

        # Database error or user does not exist.
        if not rows:
            return None

        user_nric, password_hash, role = rows[0]

        return User(
            nric=str(user_nric),
            password_hash=str(password_hash),
            role=str(role)
        )