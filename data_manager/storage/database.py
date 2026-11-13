from abc import ABC, abstractmethod

from psycopg import sql


class Database(ABC):
    @abstractmethod
    def fetch_rows(self, sql_statement: str | sql.Composed, parameters: tuple) -> list[tuple] | None:
        pass

    @abstractmethod
    def execute(self, sql_statement: str | sql.Composed, parameters: dict) -> str | None:
        pass
