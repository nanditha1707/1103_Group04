from data_manager.security import KeyCheckStore

from .database import Database


class PostgresKeyCheckStore(KeyCheckStore):
    """
    Keeps the check value in the encryption_check table, 
    which only ever has one row.
    """

    def __init__(
        self, database: Database
    ):
        self.__database = database

    def get_check_values(self) -> list[str] | None:
        sql_statement = "SELECT check_value FROM encryption_check WHERE id = 1"
        rows = self.__database.fetch_rows(sql_statement, ())
        if rows is None:
            return None

        # The table holds at most one row: (check_value,).
        if not rows:
            return []

        return [rows[0][0]]

    def save_check_value(self, check_value: str) -> str | None:
        # Edge case guard. It saves the key check value, but if there is a conflict, 
        # possibly due to two users starting the program for the first time at the same time, 
        # only the first inserted check value will be kept.
        sql_statement = """
            INSERT INTO encryption_check (id, check_value)
            VALUES (1, %(check_value)s)
            ON CONFLICT (id) DO NOTHING
        """
        # Executes the sql statement.
        return self.__database.execute(sql_statement, {"check_value": check_value})
