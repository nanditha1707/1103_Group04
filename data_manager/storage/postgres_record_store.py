import pandas as pd
from psycopg import sql

from typedefs import QueueNumberSource

from .database import Database
from .record_store import RecordStore
from .route_counter import RouteCounter


class PostgresRecordStore(RecordStore, RouteCounter, QueueNumberSource):
    def __init__(
        self, database: Database, table_name: str
    ):
        self.__database = database
        self.__table = sql.Identifier(table_name)

    def save(self, record: dict) -> str | None:
        sql_statement = self.__insert_statement(list(record))
        return self.__database.execute(sql_statement, record)

    def __insert_statement(self, columns: list[str]) -> sql.Composed:
        """Build the INSERT for a record with the given columns, e.g.
        INSERT INTO "patient_records" ("date", "primary_diagnosis_icd11_code")
        VALUES (%(date)s, %(primary_diagnosis_ICD11_Code)s)
        Each database column name is the lowercase key, the same as in
        __select_columns. Each placeholder keeps the original key so psycopg
        fills it with the matching value from the record.
        sql.Identifier and sql.Placeholder quote each name safely."""
        column_names = sql.SQL(", ").join(
            sql.Identifier(column.lower()) for column in columns
        )
        placeholders = sql.SQL(", ").join(
            sql.Placeholder(column) for column in columns
        )
        return sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            self.__table, column_names, placeholders
        )

    @staticmethod
    def __select_columns(columns: list[str]) -> sql.Composed:
        """Build the column list of a SELECT, e.g. name AS "name", ...
        The AS keeps the original names (e.g. primary_diagnosis_ICD11_Code)
        as the table headers instead of the lowercase database names.
        sql.Identifier quotes each name safely."""
        select_parts = []
        for column in columns:
            select_part = sql.SQL("{} AS {}").format(
                sql.Identifier(column.lower()),
                sql.Identifier(column)
            )
            select_parts.append(select_part)

        return sql.SQL(", ").join(select_parts)

    def __fetch_table(
        self,
        sql_statement: sql.Composed,
        parameters: tuple,
        columns: list[str]
    ) -> pd.DataFrame | None:
        rows = self.__database.fetch_rows(sql_statement, parameters)
        if rows is None:
            return None

        # The DataFrame is only used to print the table or export it to CSV.
        return pd.DataFrame(rows, columns=columns)

    def find_by_queue(self, queue_number: str, columns: list[str], date: str) -> pd.DataFrame | None:
        sql_statement = sql.SQL(
            "SELECT {} FROM {} WHERE queue_number = %s AND date = %s"
        ).format(self.__select_columns(columns), self.__table)

        return self.__fetch_table(sql_statement, (queue_number, date), columns)

    def find_by_date(self, columns: list[str], date: str) -> pd.DataFrame | None:
        sql_statement = sql.SQL(
            "SELECT {} FROM {} WHERE date = %s ORDER BY time"
        ).format(self.__select_columns(columns), self.__table)

        return self.__fetch_table(sql_statement, (date,), columns)

    def count_each_route(self, date: str) -> dict[str, int] | None:
        sql_statement = sql.SQL("""
            SELECT route, COUNT(*)
            FROM {}
            WHERE date = %s
            GROUP BY route
        """).format(self.__table)
        rows = self.__database.fetch_rows(sql_statement, (date,))
        if rows is None:
            return None

        # Each row is (route, count).
        return dict(rows)

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
