import os

from dotenv import load_dotenv

from data_manager import constants
from data_manager.storage import Database, PostgresDatabase

from .auth_service import AuthService
from .postgres_user_repository import PostgresUserRepository


class AuthFactory:
    """Creates the authentication service used by the program."""

    @staticmethod
    def create(database: Database | None = None) -> AuthService:

        if database is None:
            load_dotenv(override=True)

            database_url = os.getenv(
                constants.DATABASE_URL_ENV_VAR
            )

            database = PostgresDatabase(database_url)

        user_repository = PostgresUserRepository(database)

        return AuthService(user_repository)