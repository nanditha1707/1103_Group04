import pandas as pd
from psycopg import sql

from .database import Database
from .record_reader import RecordReader


class PostgresRecordReader(RecordReader):
    """Finds patient records in the records table."""

    def __init__(
        self, database: Database, table_name: str
    ):
        self.__database = database
        self.__table = sql.Identifier(table_name)

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

        # The DataFrame is used to show the table, export it to CSV,
        # or count the medicines for the reports.
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
