from collections.abc import Callable
from datetime import datetime

import pandas as pd

from data_manager import constants
from data_manager.patients import PatientQuery, QueryExporter, RecordSaver
from data_manager.dataset import Dataset
from data_manager.reports import ReportGenerator
from data_manager.storage import QueueNumberSource


class DataManager(QueueNumberSource):
    def __init__(
        self, icd_dataset: Dataset, hsa_dataset: Dataset, symptom_dataset: Dataset, record_saver: RecordSaver, patient_query: PatientQuery, query_exporter: QueryExporter, report_generator: ReportGenerator, queue_numbers: QueueNumberSource, clock: Callable[[], datetime]
    ):
        self.__icd_dataset = icd_dataset
        self.__hsa_dataset = hsa_dataset
        self.__symptom_dataset = symptom_dataset
        self.__record_saver = record_saver
        self.__patient_query = patient_query
        self.__query_exporter = query_exporter
        self.__report_generator = report_generator
        self.__queue_numbers = queue_numbers
        self.__clock = clock

    def get_cleaned_datasets(self) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
        """Load and clean the ICD-11 and HSA datasets. Either one is None
        if its file fails to load."""
        return (
            self.__icd_dataset.load_cleaned(),
            self.__hsa_dataset.load_cleaned()
        )

    def load_symptoms(self) -> list[str]:
        """Reads the symptoms dataset. Returns all symptom names in
        uppercase since user input is uppercased before matching."""
        symptoms_df = self.__symptom_dataset.load_cleaned()

        if symptoms_df is None:
            return []

        return symptoms_df["term"].tolist()

    def export_record(
        self,
        all_user_responses: dict,
        ai_output: dict,
        logic_result: dict
    ) -> str | None:
        """Save a completed patient record to the database. Return None
        if saved, or the error message if it could not be written."""
        return self.__record_saver.save(all_user_responses, ai_output, logic_result)

    def get_highest_queue_number(self, prefix: str, date: str) -> int | None:
        return self.__queue_numbers.get_highest_queue_number(prefix, date)

    @staticmethod
    def get_record_columns() -> list[str]:
        """Return every column of a patient record, in the order they
        are saved."""
        return list(constants.RECORD_COLUMNS)

    def get_current_date(self) -> str:
        """Return today's date from the clock as YYYY-MM-DD, the same
        format as the date column in the patient records."""
        return self.__clock().strftime("%Y-%m-%d")

    def get_patient_by_queue(
        self,
        queue_number: str,
        filter_columns: list[str],
        date: str
    ) -> pd.DataFrame | None:
        """Find the patient with the given queue number on the given date
        (YYYY-MM-DD) in the database. Return a DataFrame of their record
        with only the filter_columns, which is empty if no patient matches,
        or None if the database could not be reached."""
        return self.__patient_query.find_by_queue(queue_number, filter_columns, date)

    def get_patients_by_date(self, filter_columns: list[str], date: str) -> pd.DataFrame | None:
        """Find every patient registered on the given date (YYYY-MM-DD) in
        the database, earliest first. Return a DataFrame with one row per
        patient, which is empty if there were no patients, or None if the
        database could not be reached."""
        return self.__patient_query.find_by_date(filter_columns, date)

    def export_query(self, query_df: pd.DataFrame) -> bool:
        """Save the query results to a new timestamped CSV in the query
        folder. Return True if saved, False if the file could not be
        written."""
        return self.__query_exporter.export(query_df)

    def get_medicine_count(self, medicine: str, date: str) -> dict[str, int] | None:
        """Return a dict with how many times a specific medicine was
        issued on a given date. Returns an empty dict if it was not
        issued, or None if the database could not be reached."""
        return self.__report_generator.get_medicine_count(medicine, date)

    def get_medicine_breakdown(self, date: str) -> dict[str, int] | None:
        """Return a dict of each medicine issued on a given date and how
        many times it was issued, most issued first. Returns None if the
        database could not be reached."""
        return self.__report_generator.get_medicine_breakdown(date)

    def get_patient_type_breakdown(self, date: str) -> dict[str, int] | None:
        """Return how many Emergency, Doctor, Pharmacy and Retail patients
        there were on a given date. Returns None if the database could
        not be reached."""
        return self.__report_generator.get_patient_type_breakdown(date)
