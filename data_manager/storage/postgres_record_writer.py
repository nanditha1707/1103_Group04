from psycopg import sql

from .database import Database
from .record_writer import RecordWriter


class PostgresRecordWriter(RecordWriter):
    """Saves patient records into the records table."""

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
        PostgresRecordReader. Each placeholder keeps the original key so
        psycopg fills it with the matching value from the record.
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
