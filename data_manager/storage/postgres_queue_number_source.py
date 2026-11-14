from psycopg import sql

from .database import Database


class PostgresQueueNumberSource:
    """Finds the highest queue number given out on a date in the records
    table. The queue_number column is not encrypted.

    It has no base class. It fits the QueueNumberSource Protocol in typedefs
    because it has a matching get_highest_queue_number method."""

    def __init__(
        self, database: Database, table_name: str
    ):
        self.__database = database
        self.__table = sql.Identifier(table_name)

    def get_highest_queue_number(self, prefix: str, date: str) -> int | None:
        # SUBSTRING(... FROM '[0-9]+$') keeps only the trailing digits,
        # so it works for prefixes of any length: "D007" -> "007", "PR013" -> "013".
        # CAST(... AS INTEGER) turns "007" into 7, and MAX keeps the highest.
        # The ~ pattern only keeps queue numbers like D007 (the prefix then
        # digits only), so corrupted queue numbers are skipped.
        sql_statement = sql.SQL("""
            SELECT MAX(CAST(SUBSTRING(queue_number FROM '[0-9]+$') AS INTEGER))
            FROM {}
            WHERE date = %s AND queue_number ~ %s
        """).format(self.__table)
        queue_number_pattern = f"^{prefix}[0-9]+$"
        rows = self.__database.fetch_rows(sql_statement, (date, queue_number_pattern))
        if rows is None:
            return None

        highest_number = rows[0][0]
        if highest_number is None:
            return 0

        return highest_number
