from typing import override

from psycopg import sql

from data_manager.storage import Database


class FakeDatabase(Database):
    def __init__(
        self, rows: list[tuple] | None, save_error: str | None = None
    ) -> None:
        self.__rows = rows
        self.__save_error = save_error
        self.__fetched: list[tuple] = []
        self.__executed: list[tuple] = []

    @property
    def fetched(self) -> list[tuple]:
        return list(self.__fetched)

    @property
    def fetched_parameters(self) -> list[tuple]:
        return [parameters for _, parameters in self.__fetched]

    @property
    def executed(self) -> list[tuple]:
        return list(self.__executed)

    @override
    def fetch_rows(self, sql_statement: str | sql.Composed, parameters: tuple) -> list[tuple] | None:
        self.__fetched.append((sql_statement, parameters))
        return self.__rows

    @override
    def execute(self, sql_statement: str | sql.Composed, parameters: dict) -> str | None:
        self.__executed.append((sql_statement, parameters))
        return self.__save_error
