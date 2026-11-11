import psycopg
from psycopg import sql

from .database import Database


class PostgresDatabase(Database):
    def __init__(
        self, database_url: str | None
    ):
        self.__database_url = database_url

    def __connect(self) -> psycopg.Connection:
        if not self.__database_url:
            raise psycopg.OperationalError("no database URL was given")

        return psycopg.connect(self.__database_url)

    def fetch_rows(self, sql_statement: str | sql.Composed, parameters: tuple) -> list[tuple] | None:
        """Run a SELECT on the cloud database and return every row it found.
        Each call opens a new connection, so the rows always include records
        saved by other users. Return None if the database could not be
        reached or the query failed."""
        try:
            with self.__connect() as connection, connection.cursor() as cursor:
                # psycopg fills in each %s with the matching parameter
                # safely, so user input is never pasted into the SQL itself.
                cursor.execute(sql_statement, parameters)
                return cursor.fetchall()
        except psycopg.Error:
            return None

    def execute(self, sql_statement: str | sql.Composed, parameters: dict) -> str | None:
        try:
            with self.__connect() as connection, connection.cursor() as cursor:
                cursor.execute(sql_statement, parameters)
        except psycopg.Error as error:
            return f"{type(error).__name__} - {error}"

        return None
