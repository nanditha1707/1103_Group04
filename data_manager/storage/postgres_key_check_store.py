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
