import pandas as pd
from psycopg import sql

from .database import Database
from .queue_number_source import QueueNumberSource
from .record_counter import RecordCounter
from .record_store import RecordStore


class PostgresRecordStore(RecordStore, RecordCounter, QueueNumberSource):
    # Each record has 4 medicine columns. unnest() turns them into 4
    # rows, one medicine per row, so they can be counted as a single
    # column. Used in the FROM part of the medicine reports.
    _MEDICINES_PER_RECORD = """
        patient_records,
        unnest(ARRAY[
            primary_diagnosis_medicine_1,
            primary_diagnosis_medicine_2,
            secondary_diagnosis_medicine_1,
            secondary_diagnosis_medicine_2
        ]) AS medicine
    """

    def __init__(
        self, database: Database
    ):
        self.__database = database

    def save(self, record: dict) -> str | None:
        sql_statement = """
            INSERT INTO patient_records (
                date,
                time,
                queue_number,
                name,
                nric,
                gender,
                birthdate,
                age,
                phone_number,
                pregnancy,
                current_symptoms,
                symptom_onset_days,
                chronic_conditions,
                current_medications,
                drug_allergies,
                primary_diagnosis_icd11_code,
                primary_diagnosis_icd11_title,
                primary_diagnosis_explanation,
                primary_diagnosis_medicine_1,
                primary_diagnosis_medicine_2,
                secondary_diagnosis_icd11_code,
                secondary_diagnosis_icd11_title,
                secondary_diagnosis_explanation,
                secondary_diagnosis_medicine_1,
                secondary_diagnosis_medicine_2,
                ai_confidence_score,
                route
            )
            VALUES (
                %(date)s,
                %(time)s,
                %(queue_number)s,
                %(name)s,
                %(nric)s,
                %(gender)s,
                %(birthdate)s,
                %(age)s,
                %(phone_number)s,
                %(pregnancy)s,
                %(current_symptoms)s,
                %(symptom_onset_days)s,
                %(chronic_conditions)s,
                %(current_medications)s,
                %(drug_allergies)s,
                %(primary_diagnosis_ICD11_Code)s,
                %(primary_diagnosis_ICD11_Title)s,
                %(primary_diagnosis_explanation)s,
                %(primary_diagnosis_medicine_1)s,
                %(primary_diagnosis_medicine_2)s,
                %(secondary_diagnosis_ICD11_Code)s,
                %(secondary_diagnosis_ICD11_Title)s,
                %(secondary_diagnosis_explanation)s,
                %(secondary_diagnosis_medicine_1)s,
                %(secondary_diagnosis_medicine_2)s,
                %(ai_confidence_score)s,
                %(route)s
            )
        """
        return self.__database.execute(sql_statement, record)

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
            "SELECT {} FROM patient_records WHERE queue_number = %s AND date = %s"
        ).format(self.__select_columns(columns))

        return self.__fetch_table(sql_statement, (queue_number, date), columns)

    def find_by_date(self, columns: list[str], date: str) -> pd.DataFrame | None:
        sql_statement = sql.SQL(
            "SELECT {} FROM patient_records WHERE date = %s ORDER BY time"
        ).format(self.__select_columns(columns))

        return self.__fetch_table(sql_statement, (date,), columns)

    def count_medicine(self, medicine: str, date: str) -> int | None:
        sql_statement = f"""
            SELECT COUNT(*)
            FROM {self._MEDICINES_PER_RECORD}
            WHERE date = %s AND medicine = %s
        """
        rows = self.__database.fetch_rows(sql_statement, (date, medicine))
        if rows is None:
            return None

        # COUNT(*) always returns exactly one row with one value.
        return rows[0][0]

    def count_each_medicine(self, date: str) -> dict[str, int] | None:
        # Empty medicine columns are skipped so they are not counted.
        sql_statement = f"""
            SELECT medicine, COUNT(*) AS times_issued
            FROM {self._MEDICINES_PER_RECORD}
            WHERE date = %s AND medicine IS NOT NULL AND medicine <> ''
            GROUP BY medicine
            ORDER BY times_issued DESC, medicine
        """
        rows = self.__database.fetch_rows(sql_statement, (date,))
        if rows is None:
            return None

        # Each row is (medicine, times_issued).
        return dict(rows)

    def count_each_route(self, date: str) -> dict[str, int] | None:
        sql_statement = """
            SELECT route, COUNT(*)
            FROM patient_records
            WHERE date = %s
            GROUP BY route
        """
        rows = self.__database.fetch_rows(sql_statement, (date,))
        if rows is None:
            return None

        # Each row is (route, count).
        return dict(rows)

    def get_highest_queue_number(self, prefix: str, date: str) -> int | None:
        # SUBSTRING(... FROM 2) drops the letter: "D007" -> "007".
        # CAST(... AS INTEGER) turns "007" into 7, and MAX keeps the highest.
        # The ~ pattern only keeps queue numbers like D007 (the letter then
        # digits only), so corrupted queue numbers are skipped.
        sql_statement = """
            SELECT MAX(CAST(SUBSTRING(queue_number FROM 2) AS INTEGER))
            FROM patient_records
            WHERE date = %s AND queue_number ~ %s
        """
        queue_number_pattern = f"^{prefix}[0-9]+$"
        rows = self.__database.fetch_rows(sql_statement, (date, queue_number_pattern))
        if rows is None:
            return None

        highest_number = rows[0][0]
        if highest_number is None:
            return 0

        return highest_number
